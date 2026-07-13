# Napkin Evaluation Framework

## What this is

A framework to measure whether NAPKIN.md docs actually produce better builds. The core question: if you give two agents the same build task, one with a napkin and one without, does the napkin agent's output come out noticeably better?

This isn't about testing the convergence loop mechanics (predictions, gap scores, exam). That's internal. This is about testing the *output* — whether the doc itself helps.

## Why it matters

The convergence loop can agree on vibes and still produce a mediocre doc. The only way to know if the napkin actually helps is to test it against a world without it. This framework makes that test repeatable.

## How it works

### 1. Ground truth pool

A set of documented projects with known outcomes — real repos with READMEs, docs, and working code. These serve as the reference for what "good" looks like.

Each ground truth entry:
```json
{
  "id": "tipping-app",
  "repo": "https://github.com/someone/tipping-app",
  "founder_context": "Brief description of the founder and their vision",
  "key_decisions": ["Lightning Network", "Svelte", "no account required"],
  "ux_scenarios": ["fan sends tip in 10 seconds", "creator sees tips real-time"]
}
```

### 2. The two-agent test

For each ground truth:

1. **Napkin agent**: An agent runs the convergence loop with a "founder" (LLM role-playing based on the ground truth). It produces a NAPKIN.md.
2. **Control agent**: An agent gets the same idea with no convergence loop — just a one-shot description. It produces a plain doc.
3. **Build phase**: Two fresh agents get the same build task — one gets the NAPKIN.md, one gets the plain doc. Both build.
4. **Compare**: Score both builds against the ground truth.

### 3. Metrics

| Metric | What it measures |
|--------|-----------------|
| Decision coverage | Did the build address the key decisions from the ground truth? |
| Architecture match | Did the build use the right architecture (framework, protocol, etc.)? |
| UX scenario coverage | Can the build handle the UX scenarios from the ground truth? |
| Rework cycles | How many rounds of "that's not what I meant" did the builder need? |
| False convergence | Did the napkin agree on something the founder didn't actually want? |
| Missing features | How much of the ground truth was missed entirely? |

### 4. Similarity scoring

Two approaches, use both:

- **Embedding similarity**: Convert the NAPKIN.md and the ground truth docs to vector embeddings, compute cosine similarity. Quick numeric score.
- **LLM comparison**: Feed both docs to an LLM and ask "how well does this napkin doc match this product's actual docs?" Returns a score + qualitative breakdown of where they diverge.

## Implementation status

**Not yet built.** This is the next thing to build after the skill is stable. The concept is proven — the convergence loop works, the docs are good — but we need to measure it to improve it.

## What this is NOT

- Not a test of the convergence loop mechanics (that's internal)
- Not a CI/CD pipeline — it's a research tool
- Not required to use Napkin — it's for improving Napkin
