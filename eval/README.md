# Napkin Evaluation Framework

## What this is

A regression testing framework for the Napkin skill. Every time the convergence loop changes — new question strategy, different gap thresholds, format tweaks, prompt adjustments — the eval measures whether the change produced better or worse docs that lead to better or worse builds.

This is not "does Napkin work?" That's a one-time question. This is "did this change improve Napkin?" That's the question that matters for iterating on the skill.

## Why it matters

The convergence loop has many tunable parameters: question strategy, gap scoring thresholds, convergence detection, exam format, NAPKIN.md structure. Each change is a hypothesis — "asking about visual references earlier will produce better docs." Without measurement, you're guessing. With measurement, you're iterating.

The framework turns skill development from "I think this is better" into "this change improved decision coverage by 12% but increased false convergence by 3%."

## How it works

### 1. Ground truth pool

A set of documented projects with known good outcomes — real repos with READMEs, working code, and clear decisions. These are the reference for what "good" looks like.

```json
{
  "id": "tipping-app",
  "repo": "https://github.com/someone/tipping-app",
  "founder_context": "Brief description of the founder and their vision",
  "key_decisions": ["Lightning Network", "Svelte", "no account required"],
  "ux_scenarios": ["fan sends tip in 10 seconds", "creator sees tips real-time"]
}
```

### 2. The two-agent build test

For each ground truth:

1. **Founder simulation**: An LLM role-plays as the founder based on the ground truth. It describes the idea as if it just came to them.
2. **Napkin convergence**: The Napkin skill (current version) runs the convergence loop with the simulated founder. Produces a NAPKIN.md.
3. **Build phase**: A fresh agent gets the NAPKIN.md and a build task. It builds the project.
4. **Score the build**: Compare the build against the ground truth.

### 3. A/B testing changes

To test whether a change to the skill improves results:

1. Run the full test with the **current skill** (baseline) across all ground truths.
2. Make your change to the skill.
3. Run the full test with the **changed skill** (candidate) across the same ground truths.
4. Compare metrics. If the candidate scores better across the board, ship the change. If it regresses on any metric, decide whether the tradeoff is worth it.

### 4. Metrics

| Metric | What it measures |
|--------|-----------------|
| Decision coverage | Did the build address the key decisions from the ground truth? |
| Architecture match | Did the build use the right architecture (framework, protocol, etc.)? |
| UX scenario coverage | Can the build handle the UX scenarios from the ground truth? |
| Rework cycles | How many rounds of "that's not what I meant" did the builder need? |
| False convergence | Did the napkin converge on something the founder didn't actually want? |
| Missing features | How much of the ground truth was missed entirely? |
| Rounds to convergence | How many questions did it take? (Fewer is better if quality holds) |

### 5. Similarity scoring

Two approaches, use both:

- **Embedding similarity**: Convert the NAPKIN.md and the ground truth docs to vector embeddings, compute cosine similarity. Quick numeric score for trend tracking.
- **LLM comparison**: Feed both docs to an LLM and ask "how well does this napkin doc match this product's actual docs?" Returns a score + qualitative breakdown of where they diverge.

## Implementation status

**Design phase.** Not yet built. The skill needs to be stable before building the eval — there's no point measuring changes to a moving target.

## What this is NOT

- Not a test of "does Napkin work" — that's a one-time validation
- Not a CI/CD pipeline — it's a research and iteration tool
- Not required to use Napkin — it's for improving the skill
- Not part of the skill itself — the skill doesn't know about the eval
