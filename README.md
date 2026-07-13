# Napkin

Turn ideas into launchpads your agent can actually build from.

You say "napkin" and ramble your idea — three words or three paragraphs. Napkin asks questions until it understands your vision as well as you do, surfacing decisions you didn't know existed. Then it ships a NAPKIN.md that doesn't just describe what you want — it orients your agent's entire reasoning process toward the best possible version of your vision.

The napkin isn't a blueprint. It's a launchpad. It lights the rocket; your building agent is the guidance system.

## Why

Every founder knows the gap: you have an idea in your head, you hand it to a builder (human or agent), and what comes back isn't what you imagined. Not because the builder is bad — because the vision never made it out of your head clearly enough.

Napkin closes that gap. The convergence loop asks questions, predicts your answers behind the scenes, and scores how close it got. When it can consistently predict what you'd say, it understands your vision — and writes it down clearly enough for any agent to build from without asking you anything else.

## How it works

1. **Give your agent the skill** — one command for agent users, or copy-paste a prompt for any LLM
2. **Say "napkin" and start talking** — type your idea, any way you want
3. **Answer questions** — Napkin asks one at a time, inferring what you don't say, surfacing decisions you didn't know existed
4. **Ship it** — get a NAPKIN.md that orients your agent toward the best possible version

The convergence loop runs behind the scenes: before each question, Napkin predicts what you'll say. After you answer, it scores the gap. When the gaps are consistently low, it runs a verification round (multiple choice exam). Pass the exam, and the napkin ships.

## What makes it different

- **Surfaces decisions, not just descriptions.** If your project needs a specific framework, protocol, or design approach, Napkin identifies that decision during the conversation — not after your agent has built halfway with the wrong foundation.
- **Best-in-class by default.** Unless you say otherwise, Napkin guides your agent to aim for the best possible outcome. Say "chat app" and your agent already knows what a great chat app looks like.
- **Adapts to you.** Some founders describe by feel. Some by specifics. Napkin infers your style from how you talk and adjusts — never asking when it can reasonably figure it out on its own.
- **Three-part outcome.** Everything you wanted + nothing you didn't want + surprises you love. The "nothing you didn't want" is just as important as the "and more."

## Get started

Two ways in. Whatever you're already using.

**Agent users** (Hermes, Claude Code, Cursor, Codex, OpenCode):
```bash
npx skills add buckZz7/napkin
```

**ChatGPT / Claude chat / any LLM:** Copy the prompt from [the website](https://buckzz7.github.io/napkin/#get) and paste it in.

## What you get

A NAPKIN.md structured to capture goals, decisions, and context — not just description:

```markdown
# Tipping App

## What this is
A lightweight tipping app for creators. Fans send value
directly — no middleman, no 10% cut.

## Key decisions
- Payment rail: Lightning Network (not Stripe) — instant,
  global, micropayment-friendly
- Framework: Svelte — real-time balance updates need
  reactive rendering, not full DOM rebuilds
- No account required to tip. Creators claim with
  their Lightning address.

## UX scenarios
1. Fan lands on creator's page, enters amount, taps send. Done in 10 seconds.
2. Creator sees incoming tip in real-time, no refresh needed.
```

Hand this to your coding agent and say: "Read NAPKIN.md and build an MVP from it." Come back later to find it built — everything you wanted, nothing you didn't, with some surprises you love.

## What Napkin is not

- **Not a builder — it gets the vision clear, your tools build it**
- **Not a chatbot — it's a structured convergence process with predictions and gap scoring**
- **Not prescriptive — it surfaces decisions, your agent makes the final call**
- **Not locked in — the NAPKIN.md works with any tool, agent, or human**

## Project structure

```
napkin/
├── SKILL.md          # Convergence loop protocol — the product
├── NAPKIN.md         # Napkin's own napkin (the project vision)
├── docs/
│   └── index.html    # Landing page
├── eval/
│   └── README.md     # Evaluation framework design (two-agent test)
└── LICENSE           # MIT
```

## License

MIT
