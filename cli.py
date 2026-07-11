#!/usr/bin/env python3
"""
Napkin CLI — turn an idea into a repo.

Usage:
    python cli.py "tipping app for creators"
    python cli.py "tipping app for creators" --private
    python cli.py                        # interactive: prompts for idea
"""

import sys
import os

from engine import run_convergence_loop
from repo import create_repo


def main():
    # Get idea from args or prompt
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        idea = " ".join(sys.argv[1:])
    else:
        idea = input("What's your idea?\n> ").strip()

    if not idea:
        print("Need an idea to work with.")
        sys.exit(1)

    private = "--private" in sys.argv

    print(f"\n{'='*60}")
    print(f"  Napkin — turning your idea into a repo")
    print(f"{'='*60}")
    print(f"\nIdea: {idea}")
    print(f"Visibility: {'private' if private else 'public'}")
    print(f"\nI'm going to ask you some questions. The maintainer agent")
    print(f"will try to predict your answers. When it can, we ship.\n")

    # Define how to ask questions via CLI
    def ask_fn(question):
        print(f"\n{'─'*50}")
        print(f"  {question}")
        print(f"{'─'*50}")
        return input("> ").strip()

    # Run the convergence loop
    napkin_md, history = run_convergence_loop(idea, ask_fn)

    # Show the napkin
    print(f"\n{'='*60}")
    print(f"  NAPKIN.md")
    print(f"{'='*60}")
    print(napkin_md)
    print(f"{'='*60}\n")

    # Ask if user wants to ship
    ship = input("Ship it? (yes/no) > ").strip().lower()
    if ship in ("yes", "y", "ship", "ship it"):
        print("\nCreating repo...")
        repo_url = create_repo(idea, napkin_md, private=private)
        print(f"\n✓ Done. Your repo: {repo_url}")
    else:
        print("\nNot shipping. Your napkin is saved locally.")
        with open("NAPKIN.md", "w") as f:
            f.write(napkin_md)
        print("Saved to ./NAPKIN.md")


if __name__ == "__main__":
    main()
