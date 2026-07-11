# Real-world founder testing

## What this is
A testing mode for Napkin that uses real, documented founders and their actual open-source projects as ground truth. One LLM role-plays as the founder based on their real public material. The engine runs convergence with no web access. Then we compare the napkin doc to what the founder actually built.

## Why
Synthetic testing tells us if the mechanics work. Real-world testing tells us if convergence actually captures a real vision. The ground truth is verifiable — the product exists, we can compare.

## Scope
**In:**
- Pick a founder and their open-source project (manual confirmation of founder)
- Automatically gather source material — their X profile, README, docs, discussions where the project is talked about
- LLM is told "you are [founder], you just came up with the idea for [project], describe it as if the concept came to you"
- The "founder" LLM answers questions based on what it knows from the gathered material
- The engine runs convergence with no web access — only knows what the Q&A reveals
- After convergence, generate a similarity score between the napkin doc and the actual repo's docs (README, docs/, etc.)
- Automated as possible — manual step is confirming the founder

**Out:**
- Gathering material that's behind paywalls or private
- Testing with founders who have no public material
- Comparing to a product that doesn't have docs
- Web access for the engine during testing
- Founders with sparse public material — skip those
- Founders who aren't vocal — only use founders with enough public material to role-play accurately

## How it works
1. Operator confirms a founder + their open-source project
2. System gathers material: X posts, repo README, docs, discussions
3. System feeds material to "founder" LLM as context
4. "Founder" LLM is told: you just came up with this idea, describe it as if it's new
5. Engine runs convergence loop — asks questions, predicts answers, scores gaps, runs exam
6. Engine has no web access during the session
7. After convergence, compare napkin doc to actual repo docs
8. Output similarity score + metrics (rounds, gaps, coverage, exam pass rate)

## Similarity scoring
Two approaches to consider:
- **LLM-based comparison:** Feed both docs to an LLM and ask "how well does this napkin doc match this product's actual docs?" Returns a score + explanation of where they diverge.
- **Embedding similarity:** Convert both docs to vector embeddings and compute cosine similarity. More objective but less nuanced — it catches word overlap but not intent match.
- Best approach is likely both: embedding for a quick numeric score, LLM comparison for qualitative breakdown.

## Preventing leakage
The "founder" LLM has full context about the real product. The engine should only learn what the Q&A reveals. To prevent leakage:
- Tune the founder prompt to stay in character as someone who just had the idea, not someone who built the product
- Trial and error — run tests, see if the engine converges too fast (meaning the founder is leaking), tweak the prompt, rerun
- If the engine consistently gets gap scores near 0.0 from round 1, that's a sign the founder is giving away too much

## Open questions
- What's the right balance between embedding and LLM-based similarity? Need to test both and compare.
- How many founders do we need in the test set for meaningful results?
