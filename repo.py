"""
Repo creation for Napkin.

Creates a GitHub repo and pushes the napkin doc + basic structure.
"""

import os
import re
import subprocess
import tempfile


def slugify(name):
    """Turn an idea string into a repo name."""
    # Take first few words, lowercase, hyphenate
    words = re.sub(r"[^a-zA-Z0-9\s]", "", name).split()[:4]
    slug = "-".join(w.lower() for w in words)
    return slug or "new-project"


def create_repo(idea, napkin_md, private=False, owner=None):
    """
    Create a GitHub repo with napkin doc and basic structure.

    Args:
        idea: str — the original idea text
        napkin_md: str — the generated NAPKIN.md content
        private: bool — whether repo is private
        owner: str — GitHub username (defaults to authenticated user)

    Returns:
        repo_url: str — URL of the created repo
    """
    repo_name = slugify(idea)
    gh_cmd = ["gh", "repo", "create", repo_name, "--public" if not private else "--private",
              "--description", f"{idea[:100]}", "--clone=false"]

    result = subprocess.run(gh_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Maybe repo already exists, try with suffix
        repo_name = f"{repo_name}-napkin"
        gh_cmd = ["gh", "repo", "create", repo_name, "--public" if not private else "--private",
                  "--description", f"{idea[:100]}", "--clone=false"]
        result = subprocess.run(gh_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to create repo: {result.stderr}")

    # Get owner if not provided
    if not owner:
        owner_result = subprocess.run(["gh", "api", "user", "--jq", ".login"],
                                      capture_output=True, text=True)
        owner = owner_result.stdout.strip()

    repo_url = f"https://github.com/{owner}/{repo_name}"

    # Create temp dir, write files, push
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write NAPKIN.md
        napkin_path = os.path.join(tmpdir, "NAPKIN.md")
        with open(napkin_path, "w") as f:
            f.write(napkin_md)

        # Write README.md
        readme_path = os.path.join(tmpdir, "README.md")
        with open(readme_path, "w") as f:
            f.write(f"# {repo_name}\n\n{napkin_md.split(chr(10))[0].replace('#', '').strip()}\n\nSee [NAPKIN.md](NAPKIN.md) for the full project vision.\n")

        # Create basic structure
        for d in ["src", "docs", "tests"]:
            os.makedirs(os.path.join(tmpdir, d), exist_ok=True)
            with open(os.path.join(tmpdir, d, ".gitkeep"), "w") as f:
                f.write("")

        # Git init and push
        subprocess.run(["git", "init"], cwd=tmpdir, check=True)
        subprocess.run(["git", "add", "."], cwd=tmpdir, check=True)
        subprocess.run(["git", "commit", "-m", "Initial napkin — project vision from idea"],
                       cwd=tmpdir, check=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=tmpdir, check=True)
        subprocess.run(["git", "remote", "add", "origin",
                       f"git@github.com:{owner}/{repo_name}.git"],
                       cwd=tmpdir, check=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], cwd=tmpdir, check=True)

    return repo_url
