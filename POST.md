I built a small Python tool to reflect with care. It records what I know, what I doubt, and what does not fit.

I initially practiced Python and pandas with an AI assistant, but the project evolved into a strictly local, private tool for reflection. I practice all my languages, spoken and programming (including English, Arabic, German, Spanish, and French), so I do not lose the threads between meanings. I reflect regularly because it helps me make sense of an uncertain world.

Writing, painting, sport, conversation, and singing are also ways of expressing. They carry weight that logic alone cannot. Yet logic clarifies the frameworks we think in, even if it cannot supply values. My working formula: a definition plus its applicability is wisdom, and applicability is where values enter.

Careful analysis cuts some errors, such as unclear words and inconsistent claims. It does not cut wrong premises or missing data.

The tool is Eigenlog, from the German eigen (“own”): a map of my own categories. It will not tell me why we exist. It is meant to help me navigate.

I am acutely aware of the risks of AI-augmented introspection. An AI critic can easily turn reflection into a performance, or atrophy unassisted thinking. To counter this, the tool enforces deliberate guardrails:
- Epistemic Tagging: I can label an entry as a Hypothesis (subject to rigorous dialectical friction) or a Subjective Truth (axiomatic feelings shielded from logical deconstruction).
- Local LLM Integration: Powered by a local model (such as Qwen 2.5 Coder via llama-server) with adjustable Heat Dials (from gentle grammar & coherence review up to forensic adversarial challenge), supporting multi-turn stateful dialogues with explicit context truncation warnings and full multilingual support.
- Cold Mode: A dedicated mode for raw, unchallenged logging or gentle copyediting, preserving the baseline of my unassisted mind.
- Semantic Delta: When I log a subject I’ve recorded before, the tool surfaces my last entry and asks how my understanding has evolved, tracking dynamic progression over static categorization.
- Data Sovereignty: True honesty requires absolute safety. A mind cannot be truly open if it fears a leak. Logs are stored in a locally locked SQLite database validated via Pydantic schemas (`LogEntry`) with owner-only permissions (0o600), completely ignored by version control. The code is public; the reflections remain strictly, cryptographically mine.

The example log in the repository is invented. My own is empty until I add real days, so I have no conclusions yet. When I do, they will be inductive: probable, not proven. Deduction only tests them.

One question I cannot settle with the same tools: what shapes the lenses I use?

I post this because some of my writing has drawn interest, and I value clarity. Every claim in the repository’s example has a status: verified, unverified, or contested. If you find a flaw in the code or the philosophy, I want to know.

Code: github.com/ykhattam/eigenlog
