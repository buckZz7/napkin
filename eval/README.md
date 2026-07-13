# Napkin Evaluation Framework

## What this is

A regression testing framework for the Napkin skill. Every time the convergence loop changes — new question strategy, different gap thresholds, format tweaks, prompt adjustments — the eval measures whether the change produced a better or worse NAPKIN.md per token of LLM spend.

## The one metric

```
score = embedding_similarity(napkin_doc, ground_truth) / tokens_consumed
```

How much vision fidelity did you get per token of LLM spend?

- Similarity goes up, tokens stay the same → ship (better quality, same cost)
- Similarity stays the same, tokens go down → ship (same quality, cheaper)
- Similarity goes down, tokens go up → revert (worse AND more expensive)
- Similarity goes up, tokens go up → ship only if the ratio improved

One number. One decision. If it goes up, the change improved the skill. If it goes down, it didn't.

## Why tokens, not rounds

Tokens are the universal unit of cost. More questions, longer questions, bigger context, exam retries — they all funnel into token count. And tokens have a direct dollar amount. Rounds don't capture question length or context growth. Tokens capture everything.

## Why embedding similarity, not build quality

Napkin's job is the doc, not the build. If you measure build quality, you're measuring the builder agent, not the napkin. Agents are getting better at turning docs into code every month — that's their improvement to make, not ours. Our job is getting them the right doc.

Embedding similarity measures: does this NAPKIN.md actually capture the founder's vision? It compares the napkin doc against the real project's docs (the ground truth) using vector embeddings and cosine similarity.

### The math

An embedding is a list of numbers representing a document's meaning. Cosine similarity measures the angle between two documents' vectors:

- **1.0** → same meaning
- **0.5** → partial overlap
- **0.0** → unrelated

You don't compute this yourself — embedding APIs (OpenAI, Cohere) give you the vectors, vector libraries compute cosine similarity in one line.

## How it works

### 1. Ground truth pool

Real projects with known good outcomes — repos with READMEs, working code, and clear decisions. These are the reference for what "good" looks like.

```json
{
  "id": "tipping-app",
  "repo": "https://github.com/someone/tipping-app",
  "founder_context": "Brief description of the founder and their vision",
  "docs_to_embed": "README + docs/ + key source files"
}
```

### 2. Baseline run

1. Simulate the founder (LLM role-plays based on ground truth)
2. Run the convergence loop → produces a NAPKIN.md
3. Count total tokens consumed during the loop
4. Embed the NAPKIN.md
5. Embed the ground truth docs
6. Compute cosine similarity
7. Baseline score = similarity / tokens

### 3. A/B test

1. Run baseline with current skill across all ground truths
2. Make a change to the skill
3. Run again with the changed skill across the same ground truths
4. Compare scores. If the ratio improved, ship the change.

### 4. Example

```
         Baseline skill     Changed skill
Tokens:    12,000              5,000
Similarity: 0.85              0.83
Score:      0.000071          0.000166

→ Ship. 2% quality drop, 58% cost drop. 2.3x more vision per token.
```

```
         Baseline skill     Changed skill
Tokens:    12,000              18,000
Similarity: 0.85              0.88
Score:      0.000071          0.000049

→ Revert. 3% quality gain, 50% cost increase. Worse ratio.
```

## Implementation status

**Design phase.** Not yet built. The skill needs to be stable before building the eval — there's no point measuring changes to a moving target.

## What this is NOT

- Not a test of "does Napkin work" — that's a one-time validation
- Not a build quality test — build quality depends on the builder agent, not the napkin
- Not a CI/CD pipeline — it's a research and iteration tool
- Not required to use Napkin — it's for improving the skill
- Not part of the skill itself — the skill doesn't know about the eval
