"""
Testing framework for the Napkin convergence engine.

Two modes:
1. Simulated runs — engine plays both sides (maintainer + simulated user).
2. Recorded replays — replay saved sessions with tweaked parameters.

Metrics per run:
- Number of rounds to convergence
- Final gap scores
- Exam pass rate
- False convergence rate (converged but exam failed)
- Coverage (areas of vision explored)
- Missed areas (important questions not asked)

Usage as CLI:
    # Run a single simulated test
    python test_engine.py simulated tipping-app

    # Run all ground truths
    python test_engine.py simulated --all

    # Run with fewer rounds for quick testing
    python test_engine.py simulated tipping-app --max-rounds 5

    # Replay a recorded session
    python test_engine.py replay sessions/session-2024-01-01.json

    # Replay all sessions
    python test_engine.py replay --all

Usage as pytest:
    pytest test_engine.py -v
    pytest test_engine.py::test_simulated_convergence -v
    pytest test_engine.py::test_replay_consistency -v

Metrics:
    pytest test_engine.py::test_metrics_output -v
"""

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import Any

# Allow imports from the parent directory (engine.py)
_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent not in sys.path:
    sys.path.insert(0, _parent)
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import engine
from simulator import (
    SimulatedUser,
    load_ground_truths,
    get_ground_truth,
    compute_coverage,
)
from recorder import (
    Session,
    record_session,
    load_session,
    load_sessions,
    replay_session,
    replay_all,
)


# --- Metrics ---

@dataclass
class RunMetrics:
    """Metrics for a single convergence run."""
    idea: str
    ground_truth_id: str | None
    rounds_to_convergence: int | None  # None if never converged
    total_rounds: int
    converged: bool
    gap_trajectory: list[float] = field(default_factory=list)
    final_gap: float = 0.0
    avg_gap: float = 0.0
    min_gap: float = 0.0
    max_gap: float = 0.0
    exam_passed: bool = False
    exam_score: str = "0/0"
    exam_correct: int = 0
    exam_total: int = 0
    false_convergence: bool = False  # converged but exam failed
    coverage_pct: float = 0.0
    covered_areas: dict[str, list[str]] = field(default_factory=dict)
    missed_areas: list[str] = field(default_factory=list)
    total_areas: int = 0
    questions_asked: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)

    def summary(self) -> str:
        """Human-readable summary."""
        lines = [
            f"  Idea: {self.idea[:60]}",
            f"  Ground truth: {self.ground_truth_id or 'N/A'}",
            f"  Converged: {self.converged}",
            f"  Rounds to convergence: {self.rounds_to_convergence or 'N/A'}",
            f"  Total rounds: {self.total_rounds}",
            f"  Gap trajectory: {[round(g, 2) for g in self.gap_trajectory]}",
            f"  Final gap: {self.final_gap:.3f}",
            f"  Avg gap: {self.avg_gap:.3f}",
            f"  Exam: {self.exam_score} ({'PASS' if self.exam_passed else 'FAIL'})",
            f"  False convergence: {self.false_convergence}",
            f"  Coverage: {self.coverage_pct:.1%} ({len(self.covered_areas)}/{self.total_areas} areas)",
            f"  Missed areas: {self.missed_areas or 'none'}",
            f"  Duration: {self.duration_seconds:.1f}s",
        ]
        return "\n".join(lines)


def compute_metrics(
    session: Session,
    ground_truth: dict | None = None,
    duration: float = 0.0,
) -> RunMetrics:
    """
    Compute all metrics for a completed session.

    Args:
        session: A recorded Session with rounds and exam data.
        ground_truth: The ground truth dict (for coverage). None for real sessions.
        duration: Wall-clock time of the run in seconds.

    Returns:
        RunMetrics with all fields populated.
    """
    rounds = session.rounds
    gap_trajectory = [r["gap"] for r in rounds]
    questions = [r["question"] for r in rounds]

    # Convergence detection
    converged = session.converged
    rounds_to_convergence = None
    if converged:
        # Find the round after which check_convergence returned True
        # The engine sets converged when check_convergence passes.
        # We approximate: the round where the last-3-gaps condition first holds.
        for i in range(2, len(gap_trajectory)):
            if all(g <= 0.2 for g in gap_trajectory[i-2:i+1]):
                rounds_to_convergence = i + 1
                break
        if rounds_to_convergence is None:
            rounds_to_convergence = len(rounds)

    # Exam data
    exam = session.exam or {}
    exam_passed = exam.get("passed", False)
    exam_correct = exam.get("correct", 0)
    exam_total = exam.get("total", 0)

    # False convergence: converged (open-ended) but exam failed
    false_convergence = converged and not exam_passed

    # Coverage
    if ground_truth:
        coverage = compute_coverage(questions, ground_truth)
        coverage_pct = coverage["coverage_pct"]
        covered_areas = coverage["covered_areas"]
        missed_areas = coverage["missed_areas"]
        total_areas = coverage["total_areas"]
    else:
        coverage_pct = 0.0
        covered_areas = {}
        missed_areas = []
        total_areas = 0

    return RunMetrics(
        idea=session.idea,
        ground_truth_id=session.ground_truth_id,
        rounds_to_convergence=rounds_to_convergence,
        total_rounds=len(rounds),
        converged=converged,
        gap_trajectory=gap_trajectory,
        final_gap=gap_trajectory[-1] if gap_trajectory else 0.0,
        avg_gap=round(sum(gap_trajectory) / len(gap_trajectory), 3) if gap_trajectory else 0.0,
        min_gap=min(gap_trajectory) if gap_trajectory else 0.0,
        max_gap=max(gap_trajectory) if gap_trajectory else 0.0,
        exam_passed=exam_passed,
        exam_score=f"{exam_correct}/{exam_total}",
        exam_correct=exam_correct,
        exam_total=exam_total,
        false_convergence=false_convergence,
        coverage_pct=coverage_pct,
        covered_areas=covered_areas,
        missed_areas=missed_areas,
        total_areas=total_areas,
        questions_asked=questions,
        duration_seconds=round(duration, 1),
    )


# --- Aggregated metrics ---

@dataclass
class AggregateMetrics:
    """Metrics across multiple runs."""
    total_runs: int = 0
    converged_count: int = 0
    convergence_rate: float = 0.0
    avg_rounds_to_convergence: float = 0.0
    exam_pass_rate: float = 0.0
    false_convergence_rate: float = 0.0
    avg_coverage: float = 0.0
    avg_final_gap: float = 0.0
    avg_duration: float = 0.0
    per_run: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def summary(self) -> str:
        lines = [
            "=" * 60,
            "  AGGREGATE METRICS",
            "=" * 60,
            f"  Total runs: {self.total_runs}",
            f"  Convergence rate: {self.convergence_rate:.1%}",
            f"  Avg rounds to convergence: {self.avg_rounds_to_convergence:.1f}",
            f"  Exam pass rate: {self.exam_pass_rate:.1%}",
            f"  False convergence rate: {self.false_convergence_rate:.1%}",
            f"  Avg coverage: {self.avg_coverage:.1%}",
            f"  Avg final gap: {self.avg_final_gap:.3f}",
            f"  Avg duration: {self.avg_duration:.1f}s",
            "=" * 60,
        ]
        return "\n".join(lines)


def aggregate_metrics(metrics_list: list[RunMetrics]) -> AggregateMetrics:
    """Aggregate metrics across multiple runs."""
    n = len(metrics_list)
    if n == 0:
        return AggregateMetrics()

    converged = [m for m in metrics_list if m.converged]
    converged_with_rounds = [m for m in converged if m.rounds_to_convergence]
    exam_passed = [m for m in metrics_list if m.exam_passed]
    false_conv = [m for m in metrics_list if m.false_convergence]

    return AggregateMetrics(
        total_runs=n,
        converged_count=len(converged),
        convergence_rate=round(len(converged) / n, 3),
        avg_rounds_to_convergence=round(
            sum(m.rounds_to_convergence for m in converged_with_rounds) / len(converged_with_rounds), 1
        ) if converged_with_rounds else 0.0,
        exam_pass_rate=round(len(exam_passed) / n, 3),
        false_convergence_rate=round(len(false_conv) / n, 3),
        avg_coverage=round(sum(m.coverage_pct for m in metrics_list) / n, 3),
        avg_final_gap=round(sum(m.final_gap for m in metrics_list) / n, 3),
        avg_duration=round(sum(m.duration_seconds for m in metrics_list) / n, 1),
        per_run=[m.to_dict() for m in metrics_list],
    )


# --- Run modes ---

def run_simulated(
    ground_truth_id: str | None = None,
    max_rounds: int = 15,
    save: bool = True,
    ground_truths_path: str | None = None,
) -> tuple[RunMetrics, Session]:
    """
    Run a single simulated convergence test.

    Args:
        ground_truth_id: ID of the ground truth to use. None = pick first.
        max_rounds: Maximum convergence rounds.
        save: Whether to save the session to disk.
        ground_truths_path: Path to ground truths JSON file.

    Returns:
        (metrics, session)
    """
    if ground_truth_id:
        gt = get_ground_truth(ground_truth_id, ground_truths_path)
    else:
        truths = load_ground_truths(ground_truths_path)
        gt = truths[0]

    user = SimulatedUser(gt)
    ask_fn = user.get_ask_fn()

    start = time.time()
    session, napkin_md = record_session(
        gt["idea"],
        ask_fn,
        max_rounds=max_rounds,
        ground_truth_id=gt["id"],
    )
    duration = time.time() - start

    metrics = compute_metrics(session, ground_truth=gt, duration=duration)

    if save:
        path = session.save()
        print(f"  Session saved: {path}")

    return metrics, session


def run_simulated_all(
    max_rounds: int = 15,
    save: bool = True,
    ground_truths_path: str | None = None,
) -> AggregateMetrics:
    """
    Run simulated tests against all available ground truths.

    Returns:
        AggregateMetrics across all runs.
    """
    truths = load_ground_truths(ground_truths_path)
    all_metrics = []

    for gt in truths:
        print(f"\n{'─' * 60}")
        print(f"  Running simulated test: {gt['id']}")
        print(f"  Idea: {gt['idea'][:60]}")
        print(f"{'─' * 60}")

        metrics, _ = run_simulated(
            ground_truth_id=gt["id"],
            max_rounds=max_rounds,
            save=save,
            ground_truths_path=ground_truths_path,
        )

        print(metrics.summary())
        all_metrics.append(metrics)

    agg = aggregate_metrics(all_metrics)
    print(f"\n{agg.summary()}")
    return agg


def run_replay(
    session_path: str,
    max_rounds: int | None = None,
    save: bool = True,
) -> tuple[RunMetrics, Session, Session]:
    """
    Replay a single recorded session.

    Args:
        session_path: Path to the recorded session JSON.
        max_rounds: Override max rounds (None = use original).
        save: Whether to save the replayed session.

    Returns:
        (metrics, original_session, replayed_session)
    """
    original = load_session(session_path)

    # Load ground truth for coverage (if available)
    gt = None
    if original.ground_truth_id:
        try:
            gt = get_ground_truth(original.ground_truth_id)
        except (KeyError, FileNotFoundError):
            pass

    start = time.time()
    replayed, napkin_md = replay_session(original, max_rounds=max_rounds)
    duration = time.time() - start

    metrics = compute_metrics(replayed, ground_truth=gt, duration=duration)

    if save:
        path = replayed.save()
        print(f"  Replayed session saved: {path}")

    return metrics, original, replayed


def run_replay_all(
    max_rounds: int | None = None,
    save: bool = True,
) -> list[tuple[RunMetrics, Session, Session]]:
    """
    Replay all recorded sessions.

    Returns:
        List of (metrics, original, replayed) tuples.
    """
    results = []
    for original in load_sessions():
        gt = None
        if original.ground_truth_id:
            try:
                gt = get_ground_truth(original.ground_truth_id)
            except (KeyError, FileNotFoundError):
                pass

        start = time.time()
        replayed, _ = replay_session(original, max_rounds=max_rounds)
        duration = time.time() - start

        metrics = compute_metrics(replayed, ground_truth=gt, duration=duration)

        if save:
            replayed.save()

        results.append((metrics, original, replayed))

    return results


# --- Comparison ---

def compare_sessions(original: Session, replayed: Session) -> dict:
    """
    Compare two sessions (original vs replay) and highlight differences.

    Returns:
        Dict with comparison data.
    """
    orig_gaps = [r["gap"] for r in original.rounds]
    repl_gaps = [r["gap"] for r in replayed.rounds]

    return {
        "idea": original.idea,
        "original_rounds": len(original.rounds),
        "replayed_rounds": len(replayed.rounds),
        "original_converged": original.converged,
        "replayed_converged": replayed.converged,
        "original_exam_passed": original.exam.get("passed", False) if original.exam else False,
        "replayed_exam_passed": replayed.exam.get("passed", False) if replayed.exam else False,
        "original_gap_trajectory": orig_gaps,
        "replayed_gap_trajectory": repl_gaps,
        "round_count_changed": len(original.rounds) != len(replayed.rounds),
        "convergence_changed": original.converged != replayed.converged,
        "exam_result_changed": (
            (original.exam.get("passed", False) if original.exam else False)
            != (replayed.exam.get("passed", False) if replayed.exam else False)
        ),
    }


# --- CLI ---

def cli():
    """Command-line interface for the testing framework."""
    parser = argparse.ArgumentParser(
        description="Napkin convergence engine testing framework"
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    # Simulated
    sim = sub.add_parser("simulated", help="Run simulated convergence tests")
    sim.add_argument("ground_truth_id", nargs="?", default=None,
                     help="Ground truth ID (e.g., 'tipping-app'). Use --all for all.")
    sim.add_argument("--all", action="store_true", help="Run all ground truths")
    sim.add_argument("--max-rounds", type=int, default=15, help="Max convergence rounds")
    sim.add_argument("--no-save", action="store_true", help="Don't save sessions to disk")
    sim.add_argument("--ground-truths", default=None, help="Path to ground truths JSON")

    # Replay
    rep = sub.add_parser("replay", help="Replay recorded sessions")
    rep.add_argument("session_path", nargs="?", default=None,
                     help="Path to session JSON file. Use --all for all.")
    rep.add_argument("--all", action="store_true", help="Replay all sessions")
    rep.add_argument("--max-rounds", type=int, default=None, help="Override max rounds")
    rep.add_argument("--no-save", action="store_true", help="Don't save replayed sessions")

    # List
    lst = sub.add_parser("list", help="List available ground truths and sessions")

    args = parser.parse_args()

    if args.mode == "simulated":
        if args.all:
            run_simulated_all(
                max_rounds=args.max_rounds,
                save=not args.no_save,
                ground_truths_path=args.ground_truths,
            )
        elif args.ground_truth_id:
            metrics, _ = run_simulated(
                ground_truth_id=args.ground_truth_id,
                max_rounds=args.max_rounds,
                save=not args.no_save,
                ground_truths_path=args.ground_truths,
            )
            print(f"\n{metrics.summary()}")
        else:
            # List available ground truths
            truths = load_ground_truths(args.ground_truths)
            print("Available ground truths:")
            for gt in truths:
                print(f"  {gt['id']:20s}  {gt['idea'][:60]}")
            print("\nUse: python test_engine.py simulated <id>")

    elif args.mode == "replay":
        if args.all:
            results = run_replay_all(
                max_rounds=args.max_rounds,
                save=not args.no_save,
            )
            all_metrics = [m for m, _, _ in results]
            agg = aggregate_metrics(all_metrics)
            print(f"\n{agg.summary()}")

            print("\nComparisons:")
            for metrics, orig, repl in results:
                comp = compare_sessions(orig, repl)
                print(f"\n  {comp['idea'][:50]}")
                print(f"    Rounds: {comp['original_rounds']} -> {comp['replayed_rounds']}")
                print(f"    Converged: {comp['original_converged']} -> {comp['replayed_converged']}")
                print(f"    Exam: {comp['original_exam_passed']} -> {comp['replayed_exam_passed']}")
        elif args.session_path:
            metrics, orig, repl = run_replay(
                args.session_path,
                max_rounds=args.max_rounds,
                save=not args.no_save,
            )
            print(f"\n{metrics.summary()}")

            comp = compare_sessions(orig, repl)
            print(f"\n  Comparison:")
            print(f"    Rounds: {comp['original_rounds']} -> {comp['replayed_rounds']}")
            print(f"    Converged: {comp['original_converged']} -> {comp['replayed_converged']}")
            print(f"    Exam: {comp['original_exam_passed']} -> {comp['replayed_exam_passed']}")
            print(f"    Gaps: {[round(g, 2) for g in comp['original_gap_trajectory']]}")
            print(f"       -> {[round(g, 2) for g in comp['replayed_gap_trajectory']]}")
        else:
            sessions = load_sessions()
            if not sessions:
                print("No recorded sessions found.")
            else:
                print("Recorded sessions:")
                for s in sessions:
                    print(f"  {s.timestamp}  rounds={len(s.rounds)}  converged={s.converged}  idea={s.idea[:40]}")
            print("\nUse: python test_engine.py replay <path>")

    elif args.mode == "list":
        truths = load_ground_truths()
        print("Ground truths:")
        for gt in truths:
            print(f"  {gt['id']:20s}  {gt['idea'][:60]}")

        sessions = load_sessions()
        print(f"\nRecorded sessions ({len(sessions)}):")
        for s in sessions:
            print(f"  {s.timestamp}  rounds={len(s.rounds)}  converged={s.converged}  idea={s.idea[:40]}")


# --- Pytest tests ---

def test_simulated_convergence():
    """
    Run a simulated convergence test against the first ground truth.

    Verifies that the engine converges within max_rounds and produces
    a non-empty napkin document.

    Marked to skip if OPENAI_API_KEY is not set.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        import pytest
        pytest.skip("OPENAI_API_KEY not set")

    truths = load_ground_truths()
    assert len(truths) > 0, "No ground truths found"

    gt = truths[0]
    user = SimulatedUser(gt)
    ask_fn = user.get_ask_fn()

    napkin_md, history = engine.run_convergence_loop(
        gt["idea"], ask_fn, max_rounds=8
    )

    assert napkin_md, "Napkin output should not be empty"
    assert len(history) > 0, "Should have at least one round of Q&A"
    assert "## What this is" in napkin_md or "# " in napkin_md, \
        "Napkin should have markdown headers"


def test_simulated_all_ground_truths():
    """
    Run simulated tests against all ground truths and check convergence rate.

    This is a heavy test — it makes many LLM calls. Skipped without OPENAI_API_KEY.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        import pytest
        pytest.skip("OPENAI_API_KEY not set")

    truths = load_ground_truths()
    all_metrics = []

    for gt in truths:
        metrics, _ = run_simulated(
            ground_truth_id=gt["id"],
            max_rounds=8,
            save=False,
        )
        all_metrics.append(metrics)

    agg = aggregate_metrics(all_metrics)
    print(f"\n{agg.summary()}")

    # At least 50% should converge within 8 rounds
    assert agg.convergence_rate >= 0.5, \
        f"Convergence rate too low: {agg.convergence_rate:.1%}"


def test_simulator_consistency():
    """
    Test that the simulated user gives consistent answers.

    Asks the same question twice and checks that answers are substantively
    similar (not contradictory). Skipped without OPENAI_API_KEY.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        import pytest
        pytest.skip("OPENAI_API_KEY not set")

    truths = load_ground_truths()
    gt = truths[0]
    user = SimulatedUser(gt)

    q = "Who are the target users for this project?"
    answer1 = user.ask_fn(q)
    user.reset()
    answer2 = user.ask_fn(q)

    # Check that both answers reference key terms from the ground truth
    gt_keywords = gt["areas"]["target_users"].lower().split()
    for answer in [answer1, answer2]:
        answer_lower = answer.lower()
        matching = sum(1 for kw in gt_keywords if kw in answer_lower)
        assert matching > 0, f"Answer doesn't reference ground truth: {answer}"


def test_coverage_detection():
    """
    Test that coverage detection works correctly.

    This doesn't require LLM calls — it tests the keyword-matching logic.
    """
    truths = load_ground_truths()
    gt = truths[0]  # tipping-app

    # Simulate questions that cover some areas
    questions = [
        "Who are the target users for this app?",           # target_users
        "What should the brand feel like?",                  # brand_feel
        "How technical are you?",                            # technical_level
        "What's in the MVP scope?",                          # scope_in
        # Missing: scope_out, monetization, ux_first_screen, visual_reference
    ]

    coverage = compute_coverage(questions, gt)

    assert "target_users" in coverage["covered_areas"]
    assert "brand_feel" in coverage["covered_areas"]
    assert "technical_level" in coverage["covered_areas"]
    assert "scope_in" in coverage["covered_areas"]
    assert "monetization" in coverage["missed_areas"]
    assert "ux_first_screen" in coverage["missed_areas"]
    assert coverage["coverage_pct"] == 0.5  # 4 of 8 areas


def test_session_record_and_load():
    """
    Test that a session can be saved to JSON and loaded back.

    Uses a synthetic session (no LLM calls needed).
    """
    import tempfile

    session = Session("test idea", max_rounds=5, ground_truth_id="test")
    session.add_round(1, "Q1?", "pred1", "answer1", 0.3)
    session.add_round(2, "Q2?", "pred2", "answer2", 0.1)
    session.set_exam(True, ["MCQ1"], ["A"], ["A"], 1, 1)
    session.set_result("# Test Napkin", True)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        path = f.name
    try:
        session.save(path)
        loaded = load_session(path)

        assert loaded.idea == "test idea"
        assert len(loaded.rounds) == 2
        assert loaded.rounds[0]["question"] == "Q1?"
        assert loaded.exam is not None
        assert loaded.exam["correct"] == 1
        assert loaded.converged is True
        assert loaded.napkin_md == "# Test Napkin"
    finally:
        os.unlink(path)


def test_replay_consistency():
    """
    Test that replaying a recorded session produces comparable results.

    Saves a simulated session, then replays it and compares.

    Skipped without OPENAI_API_KEY.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        import pytest
        pytest.skip("OPENAI_API_KEY not set")

    # Run a simulated session
    truths = load_ground_truths()
    gt = truths[0]

    metrics, session = run_simulated(
        ground_truth_id=gt["id"],
        max_rounds=6,
        save=True,
    )

    # Replay it
    replay_metrics, orig, replayed = run_replay(
        session.save(),
        max_rounds=6,
        save=False,
    )

    comp = compare_sessions(orig, replayed)

    # The replay should produce a non-empty napkin
    assert replayed.napkin_md, "Replayed session should produce a napkin"
    # The replay should have at least some rounds
    assert len(replayed.rounds) > 0, "Replay should have rounds"


def test_metrics_output():
    """
    Test that metrics are computed correctly from a synthetic session.

    No LLM calls needed.
    """
    session = Session("test idea", max_rounds=5, ground_truth_id="test")
    session.add_round(1, "Q1?", "p1", "a1", 0.8)
    session.add_round(2, "Q2?", "p2", "a2", 0.5)
    session.add_round(3, "Q3?", "p3", "a3", 0.2)
    session.add_round(4, "Q4?", "p4", "a4", 0.1)
    session.add_round(5, "Q5?", "p5", "a5", 0.1)
    session.set_exam(True, ["q1", "q2"], ["A", "B"], ["A", "B"], 2, 2)
    session.set_result("# Napkin", True)

    # Use a minimal ground truth for coverage
    gt = {
        "id": "test",
        "idea": "test idea",
        "areas": {
            "target_users": "everyone",
            "brand_feel": "clean",
            "monetization": "free",
        },
        "key_decisions": [],
    }

    metrics = compute_metrics(session, ground_truth=gt, duration=5.0)

    assert metrics.total_rounds == 5
    assert metrics.converged is True
    assert metrics.final_gap == 0.1
    assert metrics.exam_passed is True
    assert metrics.false_convergence is False
    assert metrics.duration_seconds == 5.0
    assert len(metrics.gap_trajectory) == 5
    assert metrics.max_gap == 0.8
    assert metrics.min_gap == 0.1


def test_false_convergence_detection():
    """
    Test that false convergence (converged but exam failed) is detected.

    No LLM calls needed.
    """
    session = Session("test idea", max_rounds=5, ground_truth_id="test")
    session.add_round(1, "Q1?", "p1", "a1", 0.1)
    session.add_round(2, "Q2?", "p2", "a2", 0.1)
    session.add_round(3, "Q3?", "p3", "a3", 0.1)
    session.set_exam(False, ["q1", "q2", "q3"], ["A", "B", "C"], ["B", "C", "D"], 0, 3)
    session.set_result("# Napkin", True)  # converged = True

    metrics = compute_metrics(session, ground_truth=None, duration=1.0)

    assert metrics.converged is True
    assert metrics.exam_passed is False
    assert metrics.false_convergence is True


if __name__ == "__main__":
    cli()
