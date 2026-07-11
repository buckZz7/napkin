"""
pytest fixtures for Napkin convergence engine tests.

Usage:
    pytest test_engine.py -v                    # all tests
    pytest test_engine.py -v -k "not llm"       # skip tests that need API key
    pytest test_engine.py::test_coverage_detection -v  # specific test

Environment:
    OPENAI_API_KEY — required for tests that make LLM calls (simulated, replay)
    NAPKIN_MODEL   — optional, defaults to gpt-4o
"""

import json
import os
import sys

import pytest

# Ensure the engine module and tests directory are on the path
_tests_dir = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_tests_dir)
for _p in [_parent, _tests_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)


# --- Fixtures ---

@pytest.fixture
def ground_truths():
    """Load all sample ground truths."""
    from simulator import load_ground_truths
    return load_ground_truths()


@pytest.fixture
def first_ground_truth(ground_truths):
    """The first ground truth (tipping-app)."""
    return ground_truths[0]


@pytest.fixture
def ground_truth_by_id(ground_truths):
    """Get a ground truth by ID. Usage: gt = ground_truth_by_id('tipping-app')"""
    def _get(gt_id):
        for gt in ground_truths:
            if gt["id"] == gt_id:
                return gt
        raise KeyError(f"Ground truth '{gt_id}' not found")
    return _get


@pytest.fixture
def simulated_user(first_ground_truth):
    """A SimulatedUser for the first ground truth."""
    from simulator import SimulatedUser
    return SimulatedUser(first_ground_truth)


@pytest.fixture
def make_simulated_user():
    """Factory for creating SimulatedUser instances."""
    from simulator import SimulatedUser
    def _make(ground_truth):
        return SimulatedUser(ground_truth)
    return _make


@pytest.fixture
def sample_session():
    """A synthetic session for testing (no LLM calls needed)."""
    from recorder import Session
    session = Session("test idea for fixtures", max_rounds=5, ground_truth_id="test")
    session.add_round(1, "What is this project?", "A web app", "A web app for X", 0.1)
    session.add_round(2, "Who's it for?", "Devs", "Indie developers", 0.2)
    session.add_round(3, "Brand feel?", "Minimal", "Dark and minimal", 0.1)
    session.set_exam(True, ["MCQ1", "MCQ2"], ["A", "B"], ["A", "B"], 2, 2)
    session.set_result("# Test\n\n## What this is\nA test project.", True)
    return session


@pytest.fixture
def sample_ground_truth_for_coverage():
    """A minimal ground truth for coverage testing."""
    return {
        "id": "test-coverage",
        "idea": "test project",
        "areas": {
            "target_users": "developers who want simple tools",
            "brand_feel": "dark minimal clean developer-friendly",
            "technical_level": "technical developers who know apis",
            "scope_in": "add endpoint monitor alerts scope feature",
            "scope_out": "no social no sharing no charts analytics",
            "monetization": "free tier paid subscription money cost",
            "ux_first_screen": "first screen page see land flow ux",
            "visual_reference": "look like similar reference inspired example",
        },
        "key_decisions": [],
    }


# --- Markers ---

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "llm: marks tests that require OPENAI_API_KEY for LLM calls"
    )
    config.addinivalue_line(
        "markers", "unit: marks pure unit tests with no LLM calls"
    )


def pytest_collection_modifyitems(config, items):
    """Auto-skip LLM tests if no API key, and auto-mark LLM tests."""
    has_key = bool(os.environ.get("OPENAI_API_KEY"))
    for item in items:
        # Check if any test function makes LLM calls
        # (tests that skip themselves already check, but this adds a marker)
        if "llm" in item.keywords:
            if not has_key:
                item.add_marker(pytest.mark.skip(reason="OPENAI_API_KEY not set"))


# --- CLI option for max_rounds ---

def pytest_addoption(parser):
    parser.addoption(
        "--max-rounds", action="store", default=8, type=int,
        help="Maximum convergence rounds for simulated tests"
    )


@pytest.fixture
def max_rounds(request):
    """Max rounds for convergence tests (default 8)."""
    return request.config.getoption("--max-rounds")
