# Napkin

Turn ideas into clear docs ready to build.

You say "napkin" and ramble your idea. Your agent asks you questions until it
understands what you mean. Then it ships a doc clear enough to hand to any
coding agent, LLM, or human to build from. That's it — Napkin doesn't build
it, your tools do.

## Get started

Three ways in. Whatever you're already using.

**Agent users** (Hermes, Claude Code, Cursor, Codex, OpenCode):
```bash
npx skills add buckZz7/napkin
```

**ChatGPT / Claude chat / any LLM:** Copy the prompt from
[the website](https://buckzz7.github.io/napkin/#get) and paste it in.

**CLI:**
```bash
git clone https://github.com/buckZz7/napkin.git
cd napkin
uv venv && source .venv/bin/activate
uv pip install openai
export OPENAI_API_KEY=your-key
python cli.py "tipping app for creators"
```

## Links

- Website: https://buckzz7.github.io/napkin/
- Full skill: [SKILL.md](SKILL.md)
- Project vision: [NAPKIN.md](NAPKIN.md)
