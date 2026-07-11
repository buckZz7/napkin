"""
Napkin engine — convergence loop.

Flow:
1. User writes idea (text)
2. Engine generates a question
3. Maintainer LLM answers the same question (based on accumulated context)
4. User answers
5. Engine scores the gap between maintainer answer and user answer
6. Gap feeds into next question generation
7. Repeat until convergence (maintainer consistently predicts user)
8. Generate napkin doc, create repo
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

MODEL = os.environ.get("NAPKIN_MODEL", "gpt-4o")

# --- Prompts ---

QUESTION_GEN_PROMPT = """You are Napkin, a tool that turns ideas into repos.

The user wrote this idea:
"{idea}"

So far, you've asked these questions and gotten these answers:
{history}

The maintainer agent's last prediction was: "{maintainer_prediction}"
The user's actual answer was: "{user_answer}"
Gap score (0=perfect match, 1=completely different): {gap_score}

Generate the next question to ask the user. Start broad (brand feel, target
user, success criteria, UX scenarios) and get more specific over time. Ask ONE
question. Don't repeat previous questions. If the gap was high, ask something
that will help the maintainer understand the user better in that area.

Return only the question, nothing else."""

MAINTAINER_ANSWER_PROMPT = """You are a maintainer agent for a new open-source
project. Based on what you know so far, answer this question as you think the
project creator would answer it.

The user's original idea:
"{idea}"

Previous Q&A:
{history}

Question to answer:
"{question}"

Answer as if you are the project creator. Be specific and opinionated. Don't
say "it depends" — make a choice. Keep it under 3 sentences."""

SCORE_PROMPT = """Compare these two answers to the same question about a
project idea.

Question: {question}
Answer A (maintainer prediction): {maintainer_answer}
Answer B (user's actual answer): {user_answer}

Score how different they are on a scale of 0 to 1:
- 0.0 = same answer, same intent
- 0.3 = same direction, different specifics
- 0.6 = partially overlapping, significant differences
- 1.0 = completely different

Return ONLY a number between 0 and 1."""

CONVERGENCE_CHECK_PROMPT = """You are evaluating whether a maintainer agent has
converged with the project creator's vision.

Here is the full Q&A history:
{history}

Recent gap scores (most recent last): {gap_scores}

Has the maintainer converged? Convergence means:
- The last 3 gap scores are all below 0.2
- The maintainer consistently predicts the user's answers

Answer "CONVERGED" or "NOT_CONVERGED" and nothing else."""

NAPKIN_GEN_PROMPT = """You are generating the NAPKIN.md document for a new
open-source project. This document is the north star — it captures the
project creator's vision and all decisions made during the napkin process.

Original idea:
"{idea}"

Full Q&A history:
{history}

Generate a NAPKIN.md with these sections:
1. **What this is** — one paragraph, plain language
2. **Who it's for** — target users
3. **Brand feel** — tone, personality, aesthetic direction
4. **Key decisions** — bullet list of decisions made during the process
5. **MVP scope** — what's in, what's out
6. **UX scenarios** — 2-3 concrete user flows
7. **Open questions** — things still unclear

Keep it concise. No filler. This is a working document, not marketing copy."""


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
    history_str = format_history(history)
    last = history[-1] if history else {"question": "", "maintainer": "", "user": "", "gap": 1.0}

    prompt = QUESTION_GEN_PROMPT.format(
        idea=idea,
        history=history_str,
        maintainer_prediction=last.get("maintainer", ""),
        user_answer=last.get("user", ""),
        gap_score=last.get("gap", 1.0),
    )
    return call_llm(prompt, temperature=0.8)


def maintainer_answer(idea, history, question):
    """Get the maintainer agent's prediction for the current question."""
    prompt = MAINTAINER_ANSWER_PROMPT.format(
        idea=idea,
        history=format_history(history),
        question=question,
    )
    return call_llm(prompt, temperature=0.6)


def score_gap(question, maintainer_ans, user_ans):
    """Score the gap between maintainer prediction and user answer (0=match, 1=different)."""
    prompt = SCORE_PROMPT.format(
        question=question,
        maintainer_answer=maintainer_ans,
        user_answer=user_ans,
    )
    result = call_llm(prompt, temperature=0.0)
    # Extract number
    match = re.search(r"([0-9]*\.?[0-9]+)", result)
    if match:
        return min(1.0, max(0.0, float(match.group(1))))
    return 0.5


def check_convergence(history):
    """Check if maintainer has converged with user's vision."""
    gap_scores = [h["gap"] for h in history]
    if len(gap_scores) < 3:
        return False

    prompt = CONVERGENCE_CHECK_PROMPT.format(
        history=format_history(history),
        gap_scores=gap_scores,
    )
    result = call_llm(prompt, temperature=0.0)
    return "CONVERGED" in result.upper()


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
        lines.append(f"Maintainer predicted: {h['maintainer']}")
        lines.append(f"User answered: {h['user']}")
        lines.append(f"Gap: {h['gap']}")
        lines.append("")
    return "\n".join(lines)


def run_convergence_loop(idea, ask_fn, max_rounds=15):
    """
    Run the full convergence loop.

    Args:
        idea: str — the user's initial idea text
        ask_fn: callable(question) -> str — function that asks user a question and returns their answer
        max_rounds: int — maximum question rounds before forcing convergence

    Returns:
        (napkin_md, history) — the generated napkin document and full history
    """
    history = []

    for round_num in range(1, max_rounds + 1):
        # 1. Generate question
        last_gap = history[-1]["gap"] if history else 1.0
        question = generate_question(idea, history, last_gap)

        # 2. Maintainer answers (prediction)
        m_answer = maintainer_answer(idea, history, question)

        # 3. Ask user
        u_answer = ask_fn(question)
        if not u_answer or u_answer.strip().lower() in ("skip", "idk", "pass"):
            u_answer = "(skipped)"

        # 4. Score gap
        gap = score_gap(question, m_answer, u_answer)

        # 5. Record
        history.append({
            "round": round_num,
            "question": question,
            "maintainer": m_answer,
            "user": u_answer,
            "gap": gap,
        })

        print(f"\n[Round {round_num}] Gap: {gap:.2f}")
        print(f"  Q: {question}")
        print(f"  Maintainer: {m_answer[:80]}...")
        print(f"  User: {u_answer[:80]}...")

        # 6. Check convergence
        if check_convergence(history):
            print(f"\n✓ Converged after {round_num} rounds.")
            break
    else:
        print(f"\nReached max rounds ({max_rounds}). Proceeding with current understanding.")

    # 7. Generate napkin
    napkin_md = generate_napkin(idea, history)
    return napkin_md, history
