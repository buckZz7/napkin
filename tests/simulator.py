"""
Simulated user with ground truth.

The simulator plays the role of a project creator who has a specific vision.
It answers the engine's questions based on its ground truth document — not
based on what the engine predicts. This lets us test convergence at volume
without a human.

The simulator uses the same LLM calls as the engine, but with a different
system prompt — it's roleplaying as a user with a vision, not as the agent.
"""

import json
import os
import re
import sys

from openai import OpenAI

# Allow imports from the parent directory (engine.py lives there)
_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from engine import get_client, MODEL, call_llm  # reuse the same client/model/llm as engine

# --- System prompt for the simulated user ---

USER_SYSTEM_PROMPT = """You are roleplaying as a project creator who has a very
specific vision for their project. You are NOT an AI assistant. You are a real
person with opinions, preferences, and a clear idea of what you want.

Your vision (ground truth) for this project:

{vision}

Key areas of your vision:
{areas}

Key decisions you've already made:
{decisions}

Rules:
- Answer questions based on YOUR vision, not what sounds reasonable.
- Be specific and opinionated. Don't hedge. Don't say "it depends."
- If a question is about something not in your vision, give your best guess
  based on your overall aesthetic and values, but mark it as uncertain.
- Keep answers under 3 sentences, like a real person in a chat.
- Never reveal that you are an AI or that you're roleplaying. Just be the person.
- If the engine asks something you genuinely haven't thought about, say so
  ("I haven't figured that out yet" or "I'm not sure about that").
- Stay consistent with everything you've said so far. Don't contradict yourself.
"""

EXAM_ANSWER_PROMPT = """You are the project creator. Here's a multiple choice
question about your project. Pick the option that matches YOUR vision. If none
of them match, pick D (None of the above).

Your vision:
{vision}

Question:
{question}

Previous Q&A (for consistency):
{history}

Return ONLY the letter (A, B, C, or D). Nothing else."""

AREA_KEYWORDS = {
    "target_users": ["who", "user", "audience", "target", "demographic", "customer"],
    "brand_feel": ["brand", "feel", "tone", "personality", "aesthetic", "vibe",
                   "design", "visual", "look", "font", "color", "theme", "style"],
    "technical_level": ["technical", "developer", "code", "repo", "github",
                        "programming", "how technical"],
    "scope_in": ["scope", "include", "feature", "mvp", "what's in", "what does it do"],
    "scope_out": ["not include", "exclude", "out of scope", "what's out",
                  "won't", "no subscriptions", "no crypto"],
    "monetization": ["money", "monetize", "price", "paid", "free", "cost",
                     "fee", "subscription", "revenue", "business model"],
    "ux_first_screen": ["screen", "page", "see", "first", "land", "flow",
                        "ux", "interaction", "experience", "user journey",
                        "what does the user do"],
    "visual_reference": ["reference", "look like", "similar to", "inspired by",
                         "like what", "example"],
}


class SimulatedUser:
    """
    A simulated user with a ground-truth vision.

    Provides an ask_fn(question) -> str callable compatible with the engine's
    run_convergence_loop, plus an exam_ask_fn for the verification round.
    """

    def __init__(self, ground_truth: dict, temperature: float = 0.5):
        """
        Args:
            ground_truth: dict from sample_ground_truths.json — must have
                          "idea", "vision", "areas" (dict), "key_decisions".
            temperature: LLM temperature for user answers.
        """
        self.gt = ground_truth
        self.idea = ground_truth["idea"]
        self.vision = ground_truth["vision"]
        self.areas = ground_truth.get("areas", {})
        self.decisions = ground_truth.get("key_decisions", [])
        self.temperature = temperature
        self._system = self._build_system_prompt()
        self._qa_history = []  # local Q&A for consistency context

    def _build_system_prompt(self) -> str:
        """Build the system prompt from the ground truth."""
        areas_text = "\n".join(
            f"  - {k}: {v}" for k, v in self.areas.items()
        )
        decisions_text = "\n".join(f"  - {d}" for d in self.decisions)
        return USER_SYSTEM_PROMPT.format(
            vision=self.vision,
            areas=areas_text,
            decisions=decisions_text,
        )

    def _format_local_history(self) -> str:
        """Format the local Q&A history for context consistency."""
        if not self._qa_history:
            return "(no questions asked yet)"
        lines = []
        for i, (q, a) in enumerate(self._qa_history, 1):
            lines.append(f"Q{i}: {q}")
            lines.append(f"Your answer: {a}")
            lines.append("")
        return "\n".join(lines)

    def ask_fn(self, question: str) -> str:
        """
        Answer a question from the engine as the simulated user.

        This is the callable you pass to engine.run_convergence_loop().
        """
        prompt = f"""Answer this question about your project. Be specific and
opinionated based on your vision. Keep it under 3 sentences.

Question: {question}

Your previous answers (stay consistent):
{self._format_local_history()}

Answer as the project creator:"""

        answer = call_llm(
            prompt,
            system=self._system,
            temperature=self.temperature,
        )

        self._qa_history.append((question, answer))
        return answer

    def exam_ask_fn(self, question: str) -> str:
        """
        Answer a multiple choice exam question as the simulated user.

        The engine's run_exam calls ask_fn with the full MCQ text and expects
        a single letter. We detect that and return just the letter.
        """
        # If it looks like an MCQ (has A/B/C/D options), use exam prompt
        if re.search(r'\b[A-D]\)', question):
            prompt = EXAM_ANSWER_PROMPT.format(
                vision=self.vision,
                question=question,
                history=self._format_local_history(),
            )
            result = call_llm(
                prompt,
                system=self._system,
                temperature=0.2,
            )
            match = re.search(r'[A-D]', result.upper())
            if match:
                return match.group(0)
            return "D"
        else:
            # Fall through to regular ask_fn (shouldn't happen in exam)
            return self.ask_fn(question)

    def get_ask_fn(self):
        """
        Return an ask_fn that handles both regular questions and exam MCQs.

        The engine calls ask_fn for both open-ended questions and the exam.
        During the exam, the question text contains A/B/C/D options. We route
        accordingly.
        """
        def ask(question: str) -> str:
            if re.search(r'\b[A-D]\)', question):
                return self.exam_ask_fn(question)
            return self.ask_fn(question)
        return ask

    def reset(self):
        """Reset the local Q&A history for a fresh run."""
        self._qa_history = []


def load_ground_truths(path: str | None = None) -> list[dict]:
    """
    Load sample ground truths from a JSON file.

    Args:
        path: Path to the JSON file. Defaults to sample_ground_truths.json
              in the same directory as this module.

    Returns:
        List of ground truth dicts.
    """
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "sample_ground_truths.json")
    with open(path) as f:
        return json.load(f)


def get_ground_truth(gt_id: str, path: str | None = None) -> dict:
    """Load a single ground truth by its 'id' field."""
    truths = load_ground_truths(path)
    for gt in truths:
        if gt["id"] == gt_id:
            return gt
    raise KeyError(f"Ground truth '{gt_id}' not found in {path}")


def detect_areas_covered(questions: list[str]) -> dict[str, list[str]]:
    """
    Detect which ground-truth areas were covered by the engine's questions.

    Uses keyword matching with word boundaries — if a question contains a
    keyword as a whole word, that area is considered "covered."

    Args:
        questions: List of question strings asked by the engine.

    Returns:
        Dict mapping area_name -> list of question indices that covered it.
    """
    import re
    covered: dict[str, list[str]] = {}
    for area, keywords in AREA_KEYWORDS.items():
        matching = []
        for i, q in enumerate(questions):
            q_lower = q.lower()
            for kw in keywords:
                # Use word boundary matching to avoid substring false positives
                # (e.g., "fee" matching inside "feel")
                if re.search(r'\b' + re.escape(kw) + r'\b', q_lower):
                    matching.append(f"Q{i+1}")
                    break  # one keyword match is enough per question
        if matching:
            covered[area] = matching
    return covered


def compute_coverage(questions: list[str], ground_truth: dict) -> dict:
    """
    Compute coverage and missed-area metrics.

    Args:
        questions: List of questions asked by the engine.
        ground_truth: The ground truth dict (has "areas" key).

    Returns:
        Dict with:
        - covered_areas: dict of area -> [question indices]
        - missed_areas: list of area names that weren't asked about
        - coverage_pct: fraction of areas covered (0.0 - 1.0)
    """
    all_areas = list(ground_truth.get("areas", {}).keys())
    covered = detect_areas_covered(questions)
    covered_names = set(covered.keys())
    all_names = set(all_areas)
    missed = sorted(all_names - covered_names)
    coverage_pct = len(covered_names) / len(all_names) if all_names else 1.0
    return {
        "covered_areas": covered,
        "missed_areas": missed,
        "coverage_pct": round(coverage_pct, 3),
        "total_areas": len(all_areas),
        "covered_count": len(covered_names),
    }
