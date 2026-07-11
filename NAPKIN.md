# Napkin

## What this is

Napkin turns ideas into clear docs. You say "napkin" and ramble your idea — three words or three paragraphs. Napkin asks you questions until it understands your vision as well as you do. Then it ships a NAPKIN.md that's clear enough to hand to any coding agent, LLM, or human to build from. That's it. Napkin doesn't build it — your tools do.

## Who it's for

People who get ideas all the time and want to ship fast. The kind of person who currently puts ideas in a notes app and might not get back to them. They may or may not have a GitHub account. They may or may not be technical. What they have is an idea and an agent or LLM they already use.

## Brand feel

Minimal. Like writing on a napkin — no distractions, just the idea and a brainstorm session. Somewhere between playful and serious. It should feel like a serious start to a real codebase, but not deter anyone from spitballing something random and seeing what comes out.

## Key decisions

- The napkin doc is the founder's vision in plain language. It's the deliverable.
- The format may evolve. It might need to become more agents.md-style as we learn how well agents can follow plain language. Depends on the founder's technical level and how far along the idea is.
- The founder owns what happens after shipping. Napkin gets the vision clear; it doesn't build it, deploy it, or maintain it. People already have tools for that.
- The napkin can be revisited. A founder can do a touch-base session to update the napkin as things change. Whether that's a full convergence loop again or a lighter "here's what's changed" update is still open.
- No big promises. Napkin is a sketch tool, not a build tool.
- Users don't need a GitHub account. The file is the product. If they have GitHub, Napkin pushes it to a repo. If they don't, they get the file to download or copy and hand to their coding agent.
- No dedicated chat website needed for v1. The skill IS the interface. A landing page with "give this skill to your agent" or "copy this prompt into ChatGPT" is enough. A chat website could come later.
- The convergence loop runs inside whatever tool the user already uses — Telegram, Discord, CLI, Claude, ChatGPT, Hermes. Napkin meets them where they are.

## MVP scope

**In:**
- Convergence loop (idea → questions → prediction → gap scoring → exam → ship)
- NAPKIN.md as the deliverable
- Two output paths: push to GitHub repo (if connected) or give file to copy (if not)
- Next-step guidance after shipping: "give this to your coding agent to build an MVP"
- Skill-based interface (works in any agent chat — Telegram, Discord, CLI, Claude, ChatGPT)
- CLI for standalone use
- Landing page with the skill/prompt to give to your agent
- Sub-napkins for feature ideas on existing projects

**Out:**
- Building, deploying, or maintaining anything
- A chat website where users interact with Napkin directly (future)
- Recommending or setting up agent development loops (future)
- CI/CD, project management, ongoing maintenance
- GitHub account requirement — the file works standalone

## UX scenarios

1. **The shower idea:** You're walking to work and get an idea. You type "napkin tipping app for creators" into Telegram. Over your coffee break you answer a few questions and click through a quick multiple choice exam. You say "ship it." You get a NAPKIN.md. You copy the next-step instruction, paste it into your coding agent, and it starts building. You didn't lose the idea. You didn't scaffold a project manually. You just shipped the napkin.

2. **The brain dump:** You've been thinking about something for weeks. You open the CLI and paste three paragraphs. Napkin asks questions that force you to clarify what you actually mean. Some answers come easy, some you have to think about. When it converges, the napkin doc says it better than your original brain dump did.

3. **No GitHub, no problem:** Someone who's never touched GitHub has an idea. They give the napkin skill to their ChatGPT. It runs the loop. At the end, instead of pushing to a repo, they get the file and a simple instruction: "Copy this into your coding agent and ask it to build an MVP from your napkin." They don't need to know what a repo is.

4. **The monthly touch-base:** Three months later, the project has evolved. You start a touch-base with the napkin skill. You tell it what's changed. The napkin gets updated. New contributors (human or agent) read the updated version and know where things stand.

## Open questions

- **What does the "copy this into your coding agent" instruction say?** Need to research similar product flows before deciding on exact wording and structure.
- **What goes in the repo besides NAPKIN.md?** LICENSE, .gitignore, agents.md? Not sure what's best yet.
- **Website or just landing page + skill?** Leaning toward landing page only for v1. A chat website could come later if there's demand.
- **Napkin doc format:** Plain language vs agents.md style — depends on how well agents can follow plain language. Needs testing with real builds.
- **Touch-base format:** Is it the full convergence loop again, or a lighter update flow? Maybe both — let the user choose.
