"""
Session recorder and replay tool for the Napkin convergence engine.

Saves real (or simulated) napkin sessions as structured JSON, and replays
them with tweaked engine parameters to see how convergence would change.

Session JSON schema:
{
  "id": "session-uuid",
  "timestamp": "ISO-8601",
  "idea": "the original idea",
  "ground_truth_id": "tipping-app",   # null for real sessions
  "engine_params": {
    "max_rounds": 15,
    "model": "gpt-4o"
  },
  "rounds": [
    {
      "round": 1,
      "question": "How technical are you?",
      "maintainer_prediction": "You're probably somewhat technical...",
      "user_answer": "I'm non-technical, I just want the app to handle everything.",
      "gap": 0.35
    },
    ...
  ],
  "exam": {
    "passed": true,
    "questions": [...],
    "predictions": [...],
    "answers": [...],
    "correct": 4,
    "total": 5
  },
  "napkin_md": "# Project Name\n...",
  "converged": true,
  "metrics": { ... }
}
"""

import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone

# Allow imports from the parent directory (engine.py)
_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent not in sys.path:
    sys.path.insert(0, _parent)


# --- Session class ---

class Session:
    """
    Represents a single napkin convergence session.

    Accumulates rounds, exam data, and metadata. Can be saved to / loaded
    from JSON.
    """

    def __init__(
        self,
        idea: str,
        max_rounds: int = 15,
        model: str | None = None,
        ground_truth_id: str | None = None,
    ):
        self.id = str(uuid.uuid4())
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.idea = idea
        self.ground_truth_id = ground_truth_id
        self.engine_params = {
            "max_rounds": max_rounds,
            "model": model or os.environ.get("NAPKIN_MODEL", "gpt-4o"),
        }
        self.rounds: list[dict] = []
        self.exam: dict | None = None
        self.napkin_md: str = ""
        self.converged: bool = False

    def add_round(self, round_num: int, question: str, maintainer_prediction: str,
                  user_answer: str, gap: float):
        """Record a single convergence round."""
        self.rounds.append({
            "round": round_num,
            "question": question,
            "maintainer_prediction": maintainer_prediction,
            "user_answer": user_answer,
            "gap": gap,
        })

    def set_exam(self, passed: bool, questions: list[str],
                 predictions: list[str], answers: list[str],
                 correct: int, total: int):
        """Record exam results."""
        self.exam = {
            "passed": passed,
            "questions": questions,
            "predictions": predictions,
            "answers": answers,
            "correct": correct,
            "total": total,
        }

    def set_result(self, napkin_md: str, converged: bool):
        """Set the final napkin output and convergence status."""
        self.napkin_md = napkin_md
        self.converged = converged

    def to_dict(self) -> dict:
        """Serialize to a dict for JSON output."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "idea": self.idea,
            "ground_truth_id": self.ground_truth_id,
            "engine_params": self.engine_params,
            "rounds": self.rounds,
            "exam": self.exam,
            "napkin_md": self.napkin_md,
            "converged": self.converged,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Deserialize from a dict (e.g., loaded from JSON)."""
        s = cls.__new__(cls)
        s.id = data.get("id", str(uuid.uuid4()))
        s.timestamp = data.get("timestamp", "")
        s.idea = data.get("idea", "")
        s.ground_truth_id = data.get("ground_truth_id")
        s.engine_params = data.get("engine_params", {})
        s.rounds = data.get("rounds", [])
        s.exam = data.get("exam")
        s.napkin_md = data.get("napkin_md", "")
        s.converged = data.get("converged", False)
        return s

    def save(self, path: str | None = None) -> str:
        """
        Save the session to a JSON file.

        Args:
            path: File path, or None to save to ./sessions/ with auto filename.

        Returns:
            The path the file was saved to.
        """
        if path is None:
            sessions_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "sessions"
            )
            os.makedirs(sessions_dir, exist_ok=True)
            ts = self.timestamp.replace(":", "-").replace(".", "-")
            path = os.path.join(sessions_dir, f"session-{ts}.json")

        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        return path


# --- Recording wrapper ---

class RecordingAskFn:
    """
    Wraps a real or simulated ask_fn and records every Q&A interaction.

    Usage:
        recorder = RecordingAskFn(original_ask_fn, session)
        napkin_md, history = engine.run_convergence_loop(idea, recorder.ask_fn)
        # Also need to capture predictions — see record_session() below.
    """

    def __init__(self, inner_ask_fn, session: Session):
        self.inner = inner_ask_fn
        self.session = session
        self._round_num = 0

    def ask_fn(self, question: str) -> str:
        """Call the inner ask_fn and record the interaction."""
        self._round_num += 1
        # We don't have the maintainer prediction or gap score here —
        # those are captured by record_session() which wraps the engine
        # functions directly. This method is a fallback for simple recording.
        answer = self.inner(question)
        self.session.add_round(
            self._round_num, question, "", answer, 0.0
        )
        return answer


def record_session(
    idea: str,
    ask_fn,
    max_rounds: int = 15,
    ground_truth_id: str | None = None,
) -> tuple[Session, str]:
    """
    Run a convergence loop with full recording.

    Wraps the engine's internal functions to capture predictions, gap scores,
    and exam data alongside the user's answers. This is the primary way to
    create a recorded session.

    Args:
        idea: The project idea.
        ask_fn: The ask_fn for the user (real input() or simulated user).
        max_rounds: Maximum convergence rounds.
        ground_truth_id: If this is a simulated run, the ground truth ID.

    Returns:
        (session, napkin_md) — the recorded Session object and the napkin text.
    """
    import engine

    session = Session(idea, max_rounds=max_rounds, ground_truth_id=ground_truth_id)

    # Save original functions
    orig_generate_question = engine.generate_question
    orig_maintainer_answer = engine.maintainer_answer
    orig_score_gap = engine.score_gap
    orig_run_exam = engine.run_exam
    orig_check_convergence = engine.check_convergence
    orig_generate_napkin = engine.generate_napkin

    state = {"current_question": "", "current_prediction": ""}
    exam_data = {"questions": [], "predictions": [], "answers": [], "correct": 0, "total": 0}

    def patched_generate_question(idea, history, last_gap):
        q = orig_generate_question(idea, history, last_gap)
        state["current_question"] = q
        return q

    def patched_maintainer_answer(idea, history, question):
        p = orig_maintainer_answer(idea, history, question)
        state["current_prediction"] = p
        return p

    def patched_score_gap(question, m_ans, u_ans):
        gap = orig_score_gap(question, m_ans, u_ans)
        # Record this round now that we have all pieces
        round_num = len(session.rounds) + 1
        session.add_round(round_num, question, m_ans, u_ans, gap)
        return gap

    def patched_run_exam(idea, history, inner_ask_fn):
        # Patch generate_exam_questions and predict_exam_answer to record
        orig_gen_exam = engine.generate_exam_questions
        orig_predict = engine.predict_exam_answer

        def patched_gen_exam(idea, history):
            qs = orig_gen_exam(idea, history)
            exam_data["questions"] = qs
            return qs

        def patched_predict(exam_q, idea, history):
            pred = orig_predict(exam_q, idea, history)
            exam_data["predictions"].append(pred)
            return pred

        engine.generate_exam_questions = patched_gen_exam
        engine.predict_exam_answer = patched_predict

        # Track answers by wrapping ask_fn
        def recording_ask(question):
            answer = inner_ask_fn(question)
            exam_data["answers"].append(answer.upper().strip()[0] if answer and answer.strip() else "D")
            return answer

        result = orig_run_exam(idea, history, recording_ask)

        # Restore
        engine.generate_exam_questions = orig_gen_exam
        engine.predict_exam_answer = orig_predict

        # Record exam
        correct = sum(
            1 for p, a in zip(exam_data["predictions"], exam_data["answers"])
            if p == a
        )
        total = len(exam_data["questions"])
        session.set_exam(result, exam_data["questions"],
                         exam_data["predictions"], exam_data["answers"],
                         correct, total)
        return result

    # Apply patches
    engine.generate_question = patched_generate_question
    engine.maintainer_answer = patched_maintainer_answer
    engine.score_gap = patched_score_gap
    engine.run_exam = patched_run_exam

    # Track convergence
    converged = False

    def patched_check_convergence(history):
        result = orig_check_convergence(history)
        nonlocal converged
        if result:
            converged = True
        return result

    engine.check_convergence = patched_check_convergence

    try:
        napkin_md, history = engine.run_convergence_loop(
            idea, ask_fn, max_rounds=max_rounds
        )
    finally:
        # Restore all patches
        engine.generate_question = orig_generate_question
        engine.maintainer_answer = orig_maintainer_answer
        engine.score_gap = orig_score_gap
        engine.run_exam = orig_run_exam
        engine.check_convergence = orig_check_convergence
        engine.generate_napkin = orig_generate_napkin

    session.set_result(napkin_md, converged)
    return session, napkin_md


# --- Replay ---

def load_session(path: str) -> Session:
    """Load a session from a JSON file."""
    with open(path) as f:
        data = json.load(f)
    return Session.from_dict(data)


def load_sessions(directory: str | None = None) -> list[Session]:
    """Load all session JSON files from a directory."""
    if directory is None:
        directory = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "sessions"
        )
    sessions = []
    if not os.path.isdir(directory):
        return sessions
    for fname in sorted(os.listdir(directory)):
        if fname.endswith(".json"):
            sessions.append(load_session(os.path.join(directory, fname)))
    return sessions


class ReplayAskFn:
    """
    An ask_fn that replays user answers from a recorded session.

    For each question, it finds the best-matching question in the recorded
    session (by fuzzy match) and returns the recorded answer. This lets you
    re-run the engine with different parameters (prompts, model, scoring)
    using the same user answers.

    If the engine asks a question that doesn't match any recorded question,
    it falls back to a provided fallback_ask_fn (or raises).
    """

    def __init__(self, recorded_rounds: list[dict], fallback_ask_fn=None):
        """
        Args:
            recorded_rounds: List of round dicts from a recorded session.
            fallback_ask_fn: Callable to use for unmatched questions. If None,
                             returns "(no answer available)" for unknown questions.
        """
        self.recorded = recorded_rounds
        self.fallback = fallback_ask_fn
        self._used = set()  # track used round indices
        self._index = 0

    def ask_fn(self, question: str) -> str:
        """Return the recorded answer for the closest matching question."""
        best_idx = None
        best_score = -1

        for i, r in enumerate(self.recorded):
            if i in self._used:
                continue
            score = self._similarity(question, r["question"])
            if score > best_score:
                best_score = score
                best_idx = i

        if best_idx is not None and best_score > 0.3:
            self._used.add(best_idx)
            return self.recorded[best_idx]["user_answer"]

        # No good match — use fallback
        if self.fallback:
            return self.fallback(question)
        return "(no answer available)"

    @staticmethod
    def _similarity(a: str, b: str) -> float:
        """Simple word-overlap similarity (0.0 - 1.0)."""
        a_words = set(a.lower().split())
        b_words = set(b.lower().split())
        if not a_words or not b_words:
            return 0.0
        overlap = len(a_words & b_words)
        return overlap / max(len(a_words | b_words), 1)


class ReplayExamAskFn:
    """Replays exam answers from a recorded session."""

    def __init__(self, recorded_answers: list[str]):
        self.answers = list(recorded_answers)
        self._index = 0

    def ask_fn(self, question: str) -> str:
        """Return the next recorded exam answer."""
        if self._index < len(self.answers):
            ans = self.answers[self._index]
            self._index += 1
            return ans
        return "D"


def replay_session(
    session: Session,
    max_rounds: int | None = None,
    fallback_ask_fn=None,
) -> tuple[Session, str]:
    """
    Replay a recorded session with the engine using (optionally) new parameters.

    The user's answers are replayed from the recorded session. The engine
    re-generates questions, predictions, and gap scores using current engine
    settings (model, prompts, etc.). This lets you see how different engine
    configurations would have performed with the same user answers.

    Args:
        session: A recorded Session to replay.
        max_rounds: Override max_rounds (None = use session's original).
        fallback_ask_fn: Ask_fn for questions not in the recording.

    Returns:
        (new_session, napkin_md) — the newly recorded replay session.
    """
    rounds = max_rounds or session.engine_params.get("max_rounds", 15)

    replay_ask = ReplayAskFn(session.rounds, fallback_ask_fn)
    replay_exam = ReplayExamAskFn(
        session.exam["answers"] if session.exam else []
    )

    # For the exam, we need to route MCQ questions to the exam replay
    import re

    def combined_ask_fn(question: str) -> str:
        if re.search(r'\b[A-D]\)', question):
            return replay_exam.ask_fn(question)
        return replay_ask.ask_fn(question)

    # Run with recording
    new_session, napkin_md = record_session(
        session.idea,
        combined_ask_fn,
        max_rounds=rounds,
        ground_truth_id=session.ground_truth_id,
    )

    return new_session, napkin_md


def replay_all(directory: str | None = None,
               max_rounds: int | None = None) -> list[tuple[Session, Session]]:
    """
    Replay all recorded sessions in a directory.

    Returns:
        List of (original_session, replayed_session) tuples.
    """
    sessions = load_sessions(directory)
    results = []
    for s in sessions:
        new_s, _ = replay_session(s, max_rounds=max_rounds)
        results.append((s, new_s))
    return results
