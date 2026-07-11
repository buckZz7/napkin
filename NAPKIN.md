# Napkin

## What this is

Napkin turns ideas into repos. You write down an idea — could be three words or a brain dump — and Napkin asks you questions until it understands your vision as well as you do. Then it ships a repo with that understanding as the guiding document. It's a better notes app, because your idea doesn't just sit there. It becomes a real starting point for development.

## Who it's for

People who get ideas all the time and want to ship fast. The kind of person who currently puts ideas in a notes app and might not get back to them. They want to capture an idea and turn it into something real, not just store it.

## Brand feel

Minimal. Like writing on a napkin — no distractions, just the idea and a brainstorm session. Somewhere between playful and serious. It should feel like a serious start to a real codebase, but not deter anyone from spitballing something random and seeing what comes out.

## Key decisions

- The napkin doc is the founder's vision in plain language. It's the north star for any contributor — human or agent.
- The format may evolve. It might need to become more agents.md-style as we learn how well agents can follow plain language. Depends on the founder's technical level and how far along the idea is.
- The founder owns what happens after shipping. Napkin gets you set up; it doesn't autonomously build your idea into a success.
- The napkin can be revisited. A founder can do a touch-base session to update the napkin as things change. Whether that's a full convergence loop again or a lighter "here's what's changed" update is still open.
- No big promises. Napkin is for setting you up for success, not magically building it.

## MVP scope

**In:**
- Convergence loop (idea → questions → maintainer prediction → gap scoring → ship)
- NAPKIN.md as repo's guiding document
- GitHub repo creation with basic structure
- Skill-based interface (works in any agent chat — Telegram, Discord, CLI, Claude, ChatGPT)
- CLI for standalone use

**Out:**
- Autonomous MVP building — Napkin doesn't build the product, it prepares the vision
- Recommending or setting up agent development loops (future)
- Deploying or hosting anything
- CI/CD, project management, ongoing maintenance

## UX scenarios

1. **The shower idea:** You're walking to work and get an idea. You type "napkin tipping app for creators" into Telegram. Over your coffee break you answer a few questions. By the time you're done, you have a repo with a clear vision document. You didn't lose the idea. You didn't scaffold a project manually. You just shipped the napkin.

2. **The brain dump:** You've been thinking about something for weeks. You open the CLI and paste three paragraphs. Napkin asks questions that force you to clarify what you actually mean. Some answers come easy, some you have to think about. When it converges, you realize the napkin doc says it better than your original brain dump did.

3. **The monthly touch-base:** Three months later, the project has evolved. You start a touch-base with the napkin skill. You tell it what's changed. The napkin gets updated. New contributors (human or agent) read the updated version and know where things stand.

## Open questions

- **Napkin doc format:** How much structure does it need for agents to follow? Plain language vs. agents.md style? Probably depends on the founder and the project.
- **Touch-base format:** Is it the full convergence loop again, or a lighter update flow? Maybe both — let the user choose.
- **Future:** Recommending, teaching, or providing agent development loops once the napkin exists. Not in scope now, but the natural next step.
