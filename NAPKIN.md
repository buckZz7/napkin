# Napkin

## What this is

Napkin turns ideas into docs that ignite heat-seeking missiles. You say "napkin" and ramble your idea — three words or three paragraphs. Napkin asks questions until it understands your vision as well as you do. Then it ships a NAPKIN.md that gives any coding agent the goal, the context, and the decision map to build toward the best possible version of your idea — not just a functional one.

The napkin isn't a blueprint that tells the agent exactly what to do. It's a launchpad that orients the agent's entire reasoning process. When the agent hits a fork in the road — what framework, what design approach, what tradeoff — the napkin tells them what matters and what the founder's goal is, so they can make the right call without going back and asking.

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
- **The founder owns what happens after shipping.** Napkin gets the vision clear; it doesn't build it, deploy it, or maintain it. People already have tools for that.
- **The convergence loop is the agent's partner.** When the agent reads the napkin, it should feel like a partner who understands the goal — not a contractor following a spec. The napkin orients the agent toward the founder's vision so that every decision serves it.
- **No personal or project-specific details leak.** Lessons from real projects are abstracted to transferable principles. The agent picking up the napkin doesn't need to know about other projects — it needs the principle.
- **The format may evolve.** The NAPKIN.md structure might need to change to better serve the "heat-seeking missile" goal — capturing goals, decisions, and context rather than just descriptions. This is a decision for the agent building Napkin to make based on what works.
- **The convergence loop must be structurally enforced.** Predictions and gap scores are required every turn — not optional. The LLM running the loop must not skip the protocol when it gets caught up in conversation. Format enforcement (visible score line, self-check before each response) is needed.
- **Napkin is for every handoff in the chain.** The same gap between founder and builder exists between agent and subagent, maintainer and contributor. Every delegation is a mini-napkin. The convergence loop makes the implicit explicit for the entire chain.
- **The convergence loop should test itself.** A potential quality metric: give two agents the same task, one with a napkin and one without. If the napkin is good, the napkin agent's output should be noticeably better. This is a future testing framework addition.

## MVP scope

**In:**
- Convergence loop (idea → questions → prediction → gap scoring → exam → ship) with structural enforcement of predictions and scores
- NAPKIN.md as the deliverable — structured to capture goals, decisions, and context, not just description
- Decision-surfacing: the loop identifies what decisions exist in the project and captures the founder's preferences
- Best-in-class default: the napkin guides agents toward the best possible outcome unless the founder specifies otherwise
- Adaptive question style: infer the founder's type (feel-based vs specific) and adjust
- Two output paths: push to GitHub repo (if connected) or give file to copy (if not)
- Next-step guidance after shipping: "give this to your coding agent to build an MVP"
- Skill-based interface (works in any agent chat — Telegram, Discord, CLI, Claude, ChatGPT)
- CLI for standalone use
- Landing page with the skill/prompt to give to your agent
- Sub-napkins for feature ideas on existing projects

**Out:**
- Building, deploying, or maintaining anything
- A chat website where users interact with Napkin directly (future)
- Making all technical decisions for the founder — the napkin surfaces and flags, the builder decides
- CI/CD, project management, ongoing maintenance
- GitHub account requirement — the file works standalone

## UX scenarios

1. **The shower idea:** You're walking to work and get an idea. You type "napkin tipping app for creators" into Telegram. Over your coffee break you answer a few questions — they flow naturally from your idea, not a checklist. The napkin infers you're non-technical and adjusts. It surfaces decisions you didn't know existed ("this needs real-time payments — here's what that means"). You say "ship it." You get a NAPKIN.md that orients your coding agent toward your vision. You paste it in and come back later to find it built — everything you wanted, nothing you didn't, with some surprises you love.

2. **The brain dump:** You've been thinking about something for weeks. You open the CLI and paste three paragraphs. Napkin asks questions that force you to clarify what you actually mean. Some answers come easy, some you have to think about. The napkin is inferring your style, surfacing decisions, and mapping the goal. When it converges, the napkin doc says it better than your original brain dump did — and gives the building agent a clear target to aim for.

3. **The technical founder:** Someone who knows exactly what they wants — "Nostr NIP-28 chat client, Svelte, three-pane layout." Napkin infers they're technical, skips the basics, and drills into decisions that matter: "this has real-time chat — the rendering architecture is critical. Vanilla JS will cause jank. You said Svelte — good call." The napkin captures the technical context and flags any decisions the founder might have missed.

4. **The monthly touch-base:** Three months later, the project has evolved. You start a touch-base with the napkin skill. You tell it what's changed. The napkin gets updated. New contributors (human or agent) read the updated version and know where things stand — and what decisions matter going forward.

## Open questions

- **NAPKIN.md structure:** Does the current format (What this is / Who it's for / Key decisions / etc.) serve the "heat-seeking missile" goal, or does it need rethinking? The agent building Napkin should decide this based on what produces the best builds.
- **Decision-surfacing implementation:** How does the convergence loop identify which decisions exist for a given project without a fixed checklist? The loop needs to infer the decision surface from the idea itself.
- **Convergence loop enforcement:** How to structurally enforce predictions and gap scores so the LLM doesn't skip them? Format requirements, self-checks, or other mechanisms.
- **Best-in-class default:** How does the napkin communicate "aim for best in class" to the building agent without being prescriptive about what that means for each project?
- **Testing framework:** The "two agents, one with napkin one without" quality metric — how to implement and what to measure.
- **Touch-base format:** Is it the full convergence loop again, or a lighter update flow? Maybe both — let the user choose.
- **Existing LLM memory:** How to balance the agent's existing memory of the user against the napkin's independent assessment of the project's needs? Don't let biases skip important questions.
