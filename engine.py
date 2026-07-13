"""
Napkin engine — convergence loop.

Turns fuzzy ideas into clear docs. The engine asks questions, predicts the
user's answers behind the scenes, scores the gap, and repeats until it
understands the idea as well as the user does. Then it runs a verification
round (multiple choice exam) and generates the napkin doc.

Napkin is a sketch tool — it produces clear docs, not running software.
"""

import json
import os
import re

from openai import OpenAI

client = None

def get_client():
    global client
    if client is None:
        client = OpenAI()
    return client

MODEL = os.environ.get("NAPKIN_MODEL", "gpt-4o-mini")

# --- Prompts ---

QUESTION_GEN_PROMPT = """You are Napkin, a tool that turns ideas into clear docs.

The user wrote this idea:
"{idea}"

So far, you've asked these questions and gotten these answers:
{history}

The last prediction was: "{maintainer_prediction}"
The user's actual answer was: "{user_answer}"
Gap score (0=perfect match, 1=completely different): {gap_score}
Last area of disagreement: "{last_area}"

Generate the next question to ask the user.

Rules:
- Ask ONE question. Don't ask more than one at a time.
- Don't repeat previous questions.
- If the gap was above 0.4, ask a follow-up in the SAME area. Drill into the
  disagreement. Don't move to a new topic until the gap drops below 0.3.
- If the gap was low, move to a new area.
- Start broad (technical level, who's it for, brand feel, visual references)
  and get more specific over time (UX flows, scope, edge cases).
- Ask about technical level early — it changes everything downstream.
- Before declaring convergence, ask at least one concrete grounding question
  (what does the user literally see or do).

Return only the question, nothing else."""

MAINTAINER_ANSWER_PROMPT = """You are answering a question as if you were the
project creator, based on what you know so far. Be specific and opinionated.
Don't say "it depends" — make a choice. Keep it under 3 sentences.

The user's original idea:
"{idea}"

Previous Q&A:
{history}

Question to answer:
"{question}"
"""

SCORE_PROMPT = """Compare these two answers to the same question about a
project idea. Score the gap using two criteria:

Question: {question}
Answer A (your prediction): {maintainer_answer}
Answer B (user's actual answer): {user_answer}

1. Intent match (0.0-1.0):
   - 0.0 = same answer, same intent
   - 0.1-0.2 = same direction, minor differences
   - 0.3-0.4 = some shared ground, meaningful divergence
   - 0.5-0.7 = thinking about this differently
   - 0.8-1.0 = fundamentally different

2. Specificity match (add 0.0-0.3):
   - 0.0 if specifics match
   - 0.1 if close specifics
   - 0.2 if different specifics
   - 0.3 if you predicted specifics and they had none ("I don't know")

IMPORTANT: "I don't know" or "maybe you're right" or deferring to your
prediction is NOT convergence. Score it 0.5 at best. The user not having
an answer means the vision isn't formed yet.

Final gap = intent score + specificity adjustment, capped at 1.0.

Return ONLY a number between 0 and 1."""

CONVERGENCE_CHECK_PROMPT = """Evaluate whether you have converged with the
project creator's vision.

Full Q&A history:
{history}

Recent gap scores (most recent last): {gap_scores}

Convergence means:
- The last 3 gap scores are all 0.2 or below
- You consistently predict the user's answers
- At least one grounding question was asked (what does the user see/do)

Answer "CONVERGED" or "NOT_CONVERGED" and nothing else."""

EXAM_QUESTION_PROMPT = """Generate a multiple choice verification question to
test whether you understand the user's vision for this project.

Project idea: "{idea}"
Q&A history: {history}
Area to test: "{area}"

Generate ONE multiple choice question with 4 options (A, B, C, D). Option D
should be "None of the above — something else."

Format:
QUESTION: [the question]
A) [option you predict the user would pick]
B) [plausible but wrong]
C) [plausible but wrong]
D) None of the above — something else

Return only the question and options."""

NAPKIN_GEN_PROMPT = """You are generating the NAPKIN.md document for a new
project. This document captures the project creator's vision and all decisions
made during the napkin process.

Original idea:
"{idea}"

Full Q&A history:
{history}

Generate a NAPKIN.md with these sections:
1. **What this is** — one paragraph, plain language, no marketing
2. **Who it's for** — target users, be specific
3. **Brand feel** — tone, personality, aesthetic direction
4. **Key decisions** — bullet list of decisions made during the process
5. **MVP scope** — what's in, what's out
6. **UX scenarios** — 2-3 concrete user flows
7. **Open questions** — things still unclear

Keep it concise. No filler. This is a working document, not marketing copy.

IMPORTANT: Ship the whole vision. If the napkin mentions a landing page, the
repo should have a landing page. If it mentions a CLI, include the CLI. The
napkin doc should be complete enough that a coding agent can build everything
described in it without asking the user more questions."""


def call_llm(prompt, system="You are a helpful assistant.", temperature=0.7):
    """Single LLM call, returns text."""
    resp = get_client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip() if resp.choices[0].message.content else ""


def generate_question(idea, history, last_gap):
    """Generate the next question to ask the user."""
    last = history[-1] if history else {"question": "", "maintainer": "", "user": "", "gap": 1.0}
    prompt = QUESTION_GEN_PROMPT.format(
        idea=idea,
        history=format_history(history),
        maintainer_prediction=last.get("maintainer", ""),
        user_answer=last.get("user", ""),
        gap_score=last.get("gap", 1.0),
        last_area=last.get("question", ""),
    )
    return call_llm(prompt, temperature=0.8)


def maintainer_answer(idea, history, question):
    """Get the prediction for the current question."""
    prompt = MAINTAINER_ANSWER_PROMPT.format(
        idea=idea,
        history=format_history(history),
        question=question,
    )
    return call_llm(prompt, temperature=0.6)


def score_gap(question, maintainer_ans, user_ans):
    """Score the gap between prediction and user answer (0=match, 1=different)."""
    prompt = SCORE_PROMPT.format(
        question=question,
        maintainer_answer=maintainer_ans,
        user_answer=user_ans,
    )
    result = call_llm(prompt, temperature=0.0)
    match = re.search(r"([0-9]*\.?[0-9]+)", result)
    if match:
        return min(1.0, max(0.0, float(match.group(1))))
    return 0.5


def check_convergence(history):
    """Check if converged with user's vision."""
    gap_scores = [h["gap"] for h in history]
    if len(gap_scores) < 3:
        return False
    prompt = CONVERGENCE_CHECK_PROMPT.format(
        history=format_history(history),
        gap_scores=gap_scores,
    )
    result = call_llm(prompt, temperature=0.0)
    return "CONVERGED" in result.upper()


def generate_exam_questions(idea, history):
    """Generate 3-5 multiple choice verification questions."""
    areas = ["target users", "brand feel", "scope (in vs out)", "specific UX decision", "wildcard"]
    questions = []
    for area in areas:
        prompt = EXAM_QUESTION_PROMPT.format(
            idea=idea,
            history=format_history(history),
            area=area,
        )
        result = call_llm(prompt, temperature=0.5)
        questions.append(result)
    return questions


def predict_exam_answer(exam_q, idea, history):
    """Predict which option the user will pick (A, B, C, or D)."""
    prompt = f"""You are about to ask the user this multiple choice question
about their project. Predict which option they will pick based on everything
you know.

Project idea: "{idea}"
Q&A history: {format_history(history)}

Question:
{exam_q}

Return ONLY the letter (A, B, C, or D)."""
    result = call_llm(prompt, temperature=0.3)
    match = re.search(r"[ABCD]", result.upper())
    return match.group(0) if match else "A"


def run_exam(idea, history, ask_fn):
    """Run the verification round. Returns True if passed."""
    print("\n" + "=" * 50)
    print("  Verification round (the exam)")
    print("=" * 50)
    print("  Quick multiple choice. Just pick an option.\n")

    questions = generate_exam_questions(idea, history)
    correct = 0
    total = len(questions)

    for i, q in enumerate(questions, 1):
        # Predict before asking
        prediction = predict_exam_answer(q, idea, history)

        print(f"\nQ{i}:")
        print(q)

        answer = ask_fn("Your answer (A/B/C/D): ")
        answer = answer.upper().strip()
        if not answer or answer[0] not in "ABCD":
            answer = "D"

        answer_letter = answer[0]

        if answer_letter == prediction:
            correct += 1
            print(f"  ✓ Predicted {prediction}. Correct.")
        else:
            print(f"  ✗ Predicted {prediction}. You said {answer_letter}.")
            print(f"  This is a gap — noting it.")

    print(f"\nExam results: {correct}/{total} correct.")

    if correct >= total - 1:
        print("Converged. You're ready to ship.")
        return True
    else:
        print("Missed 2+. Going back to open-ended questions for the areas you got wrong.")
        return False


def generate_napkin(idea, history):
    """Generate the NAPKIN.md document."""
    prompt = NAPKIN_GEN_PROMPT.format(
        idea=idea,
        history=format_history(history),
    )
    return call_llm(prompt, temperature=0.5)


def format_history(history):
    """Format Q&A history as readable text."""
    if not history:
        return "(no questions asked yet)"
    lines = []
    for i, h in enumerate(history, 1):
        lines.append(f"Q{i}: {h['question']}")
        lines.append(f"Predicted: {h['maintainer']}")
        lines.append(f"User answered: {h['user']}")
        lines.append(f"Gap: {h['gap']}")
        lines.append("")
    return "\n".join(lines)


def run_convergence_loop(idea, ask_fn, max_rounds=15):
    """
    Run the full convergence loop.

    Args:
        idea: str — the user's initial idea text
        ask_fn: callable(question) -> str — function that asks user a question
        max_rounds: int — maximum question rounds

    Returns:
        (napkin_md, history)
    """
    history = []

    for round_num in range(1, max_rounds + 1):
        last_gap = history[-1]["gap"] if history else 1.0
        question = generate_question(idea, history, last_gap)

        m_answer = maintainer_answer(idea, history, question)

        u_answer = ask_fn(question)
        if not u_answer or u_answer.strip().lower() in ("skip", "idk", "pass"):
            u_answer = "(skipped)"

        gap = score_gap(question, m_answer, u_answer)

        history.append({
            "round": round_num,
            "question": question,
            "maintainer": m_answer,
            "user": u_answer,
            "gap": gap,
        })

        print(f"\n[Round {round_num}] Gap: {gap:.2f}")

        if check_convergence(history):
            print(f"\nConverged after {round_num} rounds.")
            break
    else:
        print(f"\nReached max rounds ({max_rounds}). Proceeding with current understanding.")

    # Verification round (the exam)
    exam_passed = run_exam(idea, history, ask_fn)
    if not exam_passed:
        # Go back for a few more open-ended rounds
        for extra_round in range(1, 4):
            print(f"\n[Extra round {extra_round}]")
            last_gap = history[-1]["gap"] if history else 1.0
            question = generate_question(idea, history, last_gap)
            m_answer = maintainer_answer(idea, history, question)
            u_answer = ask_fn(question)
            if not u_answer or u_answer.strip().lower() in ("skip", "idk", "pass"):
                u_answer = "(skipped)"
            gap = score_gap(question, m_answer, u_answer)
            history.append({
                "round": len(history) + 1,
                "question": question,
                "maintainer": m_answer,
                "user": u_answer,
                "gap": gap,
            })
        # Run exam again
        run_exam(idea, history, ask_fn)

    # Generate napkin
    napkin_md = generate_napkin(idea, history)
    return napkin_md, history
