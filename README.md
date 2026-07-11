# Napkin

Turn ideas into repos ready for AI to develop and maintain.

## What it does

You write down an idea. Napkin asks you questions. Behind the scenes, a
maintainer agent answers the same questions. When the maintainer can predict
your answers, you're in lockstep. You ship it, and a repo is born with the
napkin as the north star.

## Install

```bash
cd /opt/data/napkin
uv venv && source .venv/bin/activate
uv pip install openai python-telegram-bot requests

export OPENAI_API_KEY=...        # or any OpenAI-compatible endpoint
export GITHUB_TOKEN=...          # for repo creation
export TELEGRAM_BOT_TOKEN=...   # for Telegram bot

python cli.py "tipping app for creators"
```

## Files

| File | What it does |
|---|---|
| `engine.py` | Convergence engine: idea → questions → maintainer prediction → compare → repeat → ship |
| `napkin.py` | Generates the NAPKIN.md document from converged understanding |
| `repo.py` | Creates GitHub repo, pushes napkin + structure |
| `cli.py` | CLI interface |
| `bot.py` | Telegram bot interface |
| `questions.py` | Question generation and scoring logic |
