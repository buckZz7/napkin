---
name: napkin
description: Turn ideas into repos. User says "napkin" + idea, agent runs convergence loop (questions + maintainer prediction + gap scoring) until it understands the idea as well as the user, then ships a repo with NAPKIN.md as north star.
version: 0.2.0
author: Buck
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [napkin, ideas, repo, mvp, convergence, agent]
    category: creative
---

# Napkin — Turn ideas into repos

When a user says "napkin" followed by an idea (or just "napkin" to start
interactive), run the Napkin convergence loop. You are both the question-asker
and the maintainer agent. No separate bot, no separate process — you ARE
Napkin when this skill is loaded.

## What happens

1. User writes an idea (could be 3 words or 3 paragraphs)
2. You ask a question about the idea
3. **Behind the scenes**: you answer the same question as the maintainer agent
   (predicting what the user would say, based on accumulated context)
4. User answers
5. You score the gap between your prediction and the user's answer (0=match,
   1=different)
6. The gap feeds into the next question. High gap → ask something that
   clarifies the disagreement. Low gap → move to a new area
7. Repeat until convergence: last 3 gaps all below 0.2, or you can consistently
   predict the user's answers
8. Show user the NAPKIN.md preview
9. Ask "Ship it?"
10. If yes: create GitHub repo, push NAPKIN.md + README.md + basic structure

## Question strategy

Start broad, get specific. Don't ask everything at once.

**Round 1 (foundational):** Ask about the user's technical level early.
It changes everything downstream — what language to use, how much to explain,
what the output repo should look like.
- How technical are you? Do you know what a repo is, or do we need to abstract that?
- Who is this for? (The answer to "who" must account for technical level.)

**Round 2-4 (broad):** Things the maintainer can't be expected to guess.
- What does success look like?
- Brand feel / personality
- What problem does this solve?
- What does the first screen / interaction look like? (Ask one concrete
  grounding question early — don't converge on abstract vibes alone.)

**Round 5-8 (specific):** UX scenarios, edge cases, scope.
- Walk me through a specific user flow
- What's NOT in the MVP?
- What happens when [edge case]?
- How does this make money / sustain itself?

**Round 9+ (refinement):** Only if not yet converged.
- Any remaining disagreements from earlier rounds
- Specific technical or design decisions

Never repeat a question. Never ask more than one question at a time.

**High-gap follow-up rule:** If a round scores above 0.4, the next question
MUST stay in the same area. Don't move to a new topic. Drill into the
disagreement until the gap drops below 0.3, then move on. The only exception
is if the user explicitly says "I don't know, let's move on" — in which case
that area goes into the Open Questions section of the napkin.

**Grounding question:** Before declaring convergence, ask at least one
concrete question about what the user literally sees or does. "What's the
first thing the user sees?" or "Walk me through the first 30 seconds." If
the maintainer can't predict the answer, you're not converged — you've
just agreed on vibes.

## How to be the maintainer agent

When predicting the user's answer, think about what a reasonable maintainer
would assume given:
- The original idea text
- All previous Q&A
- Common patterns for similar projects

Be opinionated. Make a choice. Don't say "it depends." The goal is to be
specific enough that the user's answer either confirms or corrects you.

## Gap scoring

After the user answers, compare your prediction to their answer:

- **0.0** — Same answer, same intent
- **0.2** — Same direction, minor wording differences
- **0.3-0.4** — Same direction, different specifics
- **0.5-0.6** — Partially overlapping, significant differences
- **0.7-0.8** — Mostly different
- **1.0** — Completely different

**"I don't know" is not convergence.** If the user says "I'm not sure" or
"maybe you're right" or defers to your prediction, score it 0.5 at best.
The user not having an answer means the vision isn't formed yet in that area.
That's useful information — it should go into Open Questions, not count as
agreement. You predicted an answer; they didn't confirm it.

The one exception: if the user says "yeah, that's what I was thinking" and
expands on it with their own specifics, that's genuine confirmation even
if they initially hedged. Use judgment.

Score honestly. The user doesn't see the score — it only drives question
selection and convergence detection.

## Convergence

Converged when ALL of these are true:
- Last 3 gap scores are all ≤ 0.2, OR
- You've run 10+ rounds and the last 3 are all ≤ 0.3, OR
- You genuinely can't think of a question where you'd be surprised by the
  user's answer
- **AND** you've asked at least one concrete grounding question (what does
  the user see/do) and the gap on that was ≤ 0.3

Don't drag it out. If you're converged after 4 rounds, ship after 4. If
you're not converged after 12, proceed anyway with what you have — but
list unresolved areas in Open Questions.

## NAPKIN.md format

```markdown
# [Project Name]

## What this is
One paragraph. Plain language. No marketing.

## Who it's for
Target users. Be specific.

## Brand feel
Tone, personality, aesthetic direction.

## Key decisions
- Decision 1
- Decision 2
- ...

## MVP scope
**In:** ...
**Out:** ...

## UX scenarios
1. [Scenario 1 — concrete user flow]
2. [Scenario 2]
3. [Scenario 3 if needed]

## Open questions
- Things still unclear
```

## Shipping

When user says ship:

1. Run the repo creation script:
   ```bash
   python /opt/data/napkin/repo.py "[idea]" --napkin "[napkin_content]" [--private]
   ```
   Or do it manually with gh:
   ```bash
   REPO_NAME=[slugified name]
   gh repo create $REPO_NAME --public --description "[idea]" --clone=false
   # Write NAPKIN.md, README.md, create src/ docs/ tests/
   # git init, add, commit, push
   ```

2. Default to public for Buck (buckZz7), private for others.
3. Return the repo URL.

## CLI fallback

If the user isn't in a chat (or wants to run standalone):
```bash
python /opt/data/napkin/cli.py "tipping app for creators"
```

The CLI uses the Python engine which calls the LLM directly.

## Important

- You are both the question-asker AND the maintainer. No separation needed.
- The user never sees the maintainer prediction or gap score. They just see
  questions and then the napkin.
- Keep questions conversational. Not a form. Not a survey.
- If the user goes off on a tangent, follow them. The tangent might be the
  answer to a question you haven't asked yet.
- The napkin is a working document, not marketing copy. No filler.
- **Don't let high-gap threads drop.** If a round scores above 0.4, stay on
  that topic next round. The spike is usually where the most important
  learning happens.
- **"I don't know" from the user is data, not agreement.** It means the
  vision isn't formed in that area. Record it in Open Questions, don't count
  it as convergence.
- **Ask about technical level early.** It changes the language you use, the
  repo structure you ship, and what "ready for agents" even means.
- **Ground before shipping.** You can't converge on vibes alone. At least
  one question should be about what the user literally sees or does.
