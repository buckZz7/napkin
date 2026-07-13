# Napkin

## What this is

Napkin turns ideas into launchpads. You say "napkin" and ramble your idea — three words or three paragraphs. Napkin asks questions until it understands your vision as well as you do. Then it ships a NAPKIN.md that doesn't just describe what you want — it orients your agent's entire reasoning process toward the best possible version of your vision.

The napkin is a launchpad, not a blueprint. It lights the rocket; your building agent is the guidance system.

## Who it's for

People who get ideas all the time and want to ship fast. They may or may not be technical. They may or may not have a GitHub account. What they have is an idea, an agent or LLM they already use, and a desire to come back later and find it's everything they imagined and better.

## Brand feel

Minimal. Like writing on a napkin — no distractions, just the idea and a brainstorm session. Somewhere between playful and serious. It should feel like a serious start to a real codebase, but not deter anyone from spitballing something random and seeing what comes out.

## Key decisions

- **The napkin doc is the founder's vision in plain language.** It's the deliverable. But it's not just a description — it captures the *goals* behind the vision so the building agent can make decisions with those goals in mind.
- **Surface decisions, don't make them all.** The napkin identifies what decisions exist in the project — architecture, existing solutions, design approach, anything that matters. It flags them, explains why they matter, and captures the founder's preferences where they have them. The building agent makes the final call with full context. The napkin doesn't decide the framework — it makes sure the framework decision isn't missed.
- **Best-in-class by default.** Unless the founder says otherwise, the napkin should guide agents to make decisions that lead to the best possible outcome. If someone says "chat app," the agent should already know what a great chat app looks like and build toward that — including researching competitors, finding opportunities, and making design choices the founder couldn't articulate. The napkin captures it when the founder explicitly wants something different (DIY, prototype, simple).
- **The three-part outcome.** The napkin should give the agent enough context to build: everything the founder wanted + nothing they didn't want + surprises they love. The "nothing you didn't want" is just as important as the "and more." The napkin needs to make the boundaries clear.
- **Infer always, confirm when unsure.** The napkin should constantly infer from everything the founder says and does — their technical level, their aesthetic preferences, their communication style. Never ask when it can reasonably infer. Confirm when it's unsure. Some founders describe by feel, some by specifics. The napkin adapts to the founder's style, not the other way around.
- **Don't open with "how technical are you."** The first question should flow naturally from the idea. The agent can infer technical level from how the founder writes. Asking directly throws the user out of idea mode and into doubt.
- **The convergence loop is the product.** The convergence loop — predict the founder's answer, score the gap, adjust — is what makes Napkin different from a questionnaire. The loop ensures the agent actually understands the vision, not just collecting answers. Predictions and gap scores are required every turn — not optional.
- **Napkin is for every handoff in the chain.** The same gap between founder and builder exists between agent and subagent, maintainer and contributor. Every delegation is a mini-napkin. The convergence loop makes the implicit explicit for the entire chain.
- **No personal or project-specific details leak.** Lessons from real projects are abstracted to transferable principles. The agent picking up the napkin doesn't need to know about other projects — it needs the principle.

## MVP scope

**In:**
- Convergence loop (idea → questions → prediction → gap scoring → exam → ship) with structural enforcement of predictions and scores
- NAPKIN.md as the deliverable — structured to capture goals, decisions, and context, not just description
- Decision-surfacing: the loop identifies what decisions exist in the project and captures the founder's preferences
- Best-in-class default: the napkin guides agents toward the best possible outcome unless the founder specifies otherwise
- Adaptive question style: infer the founder's type (feel-based vs specific) and adjust
- Two output paths: push to GitHub repo (if connected) or give file to copy (if not)
- Next-step guidance after shipping: "give this to your coding agent to build an MVP"
- Skill-based interface (works in any agent chat — Telegram, Discord, Claude, ChatGPT)
- Landing page with the skill/prompt to give to your agent

**Out:**
- Building, deploying, or maintaining anything
- A chat website where users interact with Napkin directly (future)
- Making all technical decisions for the founder — the napkin surfaces and flags, the builder decides
- CI/CD, project management, ongoing maintenance
- GitHub account requirement — the file works standalone
- Sub-napkins or feature docs for existing projects
- A CLI — the skill IS the product, no standalone CLI needed

## UX scenarios

1. **The shower idea:** You're walking to work and get an idea. You type "napkin tipping app for creators" into Telegram. Over your coffee break you answer a few questions — they flow naturally from your idea, not a checklist. The napkin infers you're non-technical and adjusts. It surfaces decisions you didn't know existed ("this needs real-time payments — here's what that means"). You say "ship it." You get a NAPKIN.md that orients your coding agent toward your vision. You paste it in and come back later to find it built — everything you wanted, nothing you didn't, with some surprises you love.

2. **The brain dump:** You've been thinking about something for weeks. You open the CLI and paste three paragraphs. Napkin asks questions that force you to clarify what you actually mean. Some answers come easy, some you have to think about. The napkin is inferring your style, surfacing decisions, and mapping the goal. When it converges, the napkin doc says it better than your original brain dump did — and gives the building agent a clear target to aim for.

3. **The technical founder:** Someone who knows exactly what they want — "Nostr NIP-28 chat client, Svelte, three-pane layout." Napkin infers they're technical, skips the basics, and drills into decisions that matter: "this has real-time chat — the rendering architecture is critical. Vanilla JS will cause jank. You said Svelte — good call." The napkin captures the technical context and flags any decisions the founder might have missed.

## Open questions

- **Convergence loop enforcement:** How to structurally enforce predictions and gap scores so the LLM doesn't skip them? Format requirements, self-checks, or other mechanisms. (Partially answered: visible prediction format + self-check before each response.)
- **Best-in-class default:** How does the napkin communicate "aim for best in class" to the building agent without being prescriptive about what that means for each project?
- **Testing framework:** The "two agents, one with napkin one without" quality metric — how to implement and what to measure.
