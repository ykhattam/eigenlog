"""eigenlog web — NiceGUI localhost-only glass-morphism reflection UI.

Privacy: binds strictly to 127.0.0.1, no external CDNs, no telemetry,
no cloud. Reuses PersistentMind (SQLite) and ai_critic (local LLM).
"""
import os
import sys
import html as html_mod

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nicegui import ui
from interactive_mind import PersistentMind
from ai_critic import critique, check_server, LOCAL_MODEL_NAME

DB_PATH = os.path.join(ROOT, "eigenlog.db")
mind = PersistentMind(db_path=DB_PATH)

# ---------------------------------------------------------------------------
# Glass-morphism CSS (no external assets)
# ---------------------------------------------------------------------------
ui.add_css("""
:root {
  --bg-start: #0f2b3c;
  --bg-mid:   #14354a;
  --bg-end:   #0d1b2a;
  --ink:      #e8eef5;
  --ink-dim:  #9fb3c7;
  --accent:   #7dd3fc;
  --accent-2: #a78bfa;
  --glass:    rgba(255, 255, 255, 0.06);
  --glass-2:  rgba(255, 255, 255, 0.03);
  --border:   rgba(255, 255, 255, 0.12);
  --border-2: rgba(255, 255, 255, 0.06);
  --shadow:   0 24px 60px -12px rgba(0, 0, 0, 0.5);
  --card:     rgba(20, 40, 55, 0.5);
}

body {
  background:
    radial-gradient(circle at 15% 10%, rgba(124, 58, 237, 0.14), transparent 45%),
    radial-gradient(circle at 85% 20%, rgba(6, 182, 212, 0.10), transparent 45%),
    linear-gradient(135deg, var(--bg-start) 0%, var(--bg-mid) 55%, var(--bg-end) 100%);
  background-attachment: fixed;
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  margin: 0;
  padding: 0;
}

.glass {
  background: var(--card);
  backdrop-filter: blur(22px) saturate(1.15);
  -webkit-backdrop-filter: blur(22px) saturate(1.15);
  border: 1px solid var(--border);
  border-radius: 28px;
  box-shadow: var(--shadow);
}

.panel {
  padding: 28px;
}

.glass-title {
  font-size: 2.2rem;
  font-weight: 900;
  letter-spacing: 0.02em;
  margin: 0 0 4px 0;
  text-shadow: 0 2px 14px rgba(0,0,0,0.4);
}

.subtitle {
  color: var(--ink-dim);
  font-size: 0.9rem;
  margin: 0;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

#status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 16px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  margin-top: 10px;
  backdrop-filter: blur(8px);
  border: 1px solid var(--border-2);
  background: rgba(0, 0, 0, 0.25);
}
#status.ok { color: #7dd3fc; border-color: rgba(125, 211, 252, 0.35); }
#status.down { color: #f87171; border-color: rgba(248, 113, 113, 0.35); }

.dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 8px currentColor;
  animation: pulse 2s infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.45; } }

input, textarea, select {
  width: 100%;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid var(--border-2);
  border-radius: 14px;
  padding: 11px 16px;
  font-size: 0.95rem;
  color: var(--ink);
  outline: none;
}
input:focus, textarea:focus, select:focus {
  border-color: var(--accent);
}

.btn-primary {
  background: linear-gradient(135deg, var(--accent), #38bdf8);
  color: #051a26;
  border: none;
  border-radius: 14px;
  padding: 11px 24px;
  font-size: 0.95rem;
  font-weight: 900;
  cursor: pointer;
  box-shadow: 0 12px 24px -8px rgba(125, 211, 252, 0.35);
}
.btn-primary:hover { filter: brightness(1.1); }
.btn-primary:active { transform: translateY(1px); }
.btn-primary:disabled { opacity: 0.55; cursor: not-allowed; }

.btn-secondary {
  background: rgba(255, 255, 255, 0.08);
  color: var(--ink-dim);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 11px 20px;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
}
.btn-secondary:hover { background: rgba(255, 255, 255, 0.16); color: var(--ink); }

.card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-2);
  border-radius: 22px;
  padding: 22px;
}

.entry {
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid var(--border-2);
  border-radius: 18px;
  padding: 16px 20px;
  margin-bottom: 10px;
}
.entry-meta {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 8px;
  font-size: 0.75rem;
  color: var(--ink-dim);
  margin-bottom: 6px;
}
.entry-subject {
  font-weight: 900;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-size: 0.78rem;
}
.entry-obs {
  font-size: 0.95rem;
  color: var(--ink);
  margin: 0;
  white-space: pre-wrap;
}
.entry-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 8px;
}
.tag {
  font-size: 0.68rem;
  padding: 3px 10px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-2);
  color: var(--ink-dim);
}

.empty {
  text-align: center;
  color: var(--ink-dim);
  padding: 48px 0;
  font-size: 0.95rem;
}

.chip {
  font-size: 0.72rem;
  padding: 7px 14px;
  border-radius: 12px;
  cursor: pointer;
  border: 1px solid var(--border-2);
  background: rgba(255, 255, 255, 0.05);
  color: var(--ink-dim);
  transition: all 0.2s;
}
.chip:hover { background: rgba(255, 255, 255, 0.14); color: var(--ink); }
.chip.active {
  background: var(--accent);
  color: #04171e;
  border-color: var(--accent);
}

.critique-box {
  margin-top: 10px;
  padding-top: 12px;
  border-top: 1px solid var(--border-2);
}
.critique-box pre {
  white-space: pre-wrap;
  font-family: inherit;
  font-size: 0.9rem;
  margin: 8px 0 0 0;
  color: var(--ink-dim);
  background: rgba(0, 0, 0, 0.25);
  border-radius: 14px;
  padding: 16px;
  border: 1px solid var(--border-2);
}

.msg { font-size: 0.8rem; margin-top: 8px; }
.msg.ok { color: #7dd3fc; }
.msg.err { color: #f87171; }

.side-card {
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid var(--border-2);
  border-radius: 20px;
  padding: 18px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}
.side-icon {
  width: 44px; height: 44px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid var(--border);
  display: grid; place-items: center;
  font-size: 1.5rem;
}
.side-card h3 {
  margin: 0;
  font-size: 0.78rem;
  font-weight: 900;
  color: var(--ink-dim);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

footer {
  margin-top: 30px;
  padding: 20px 0;
  border-top: 1px solid var(--border-2);
  font-size: 0.72rem;
  color: var(--ink-dim);
  text-align: center;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
footer a { color: var(--accent); text-decoration: none; border-bottom: 1px solid rgba(125,211,252,0.35); }
footer a:hover { color: #38bdf8; }

@media (max-width: 760px) {
  body { padding: 16px; }
}
""", shared=True
)

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------
HEAT_LEVEL = 2
EPISTEMIC_TAG = "hypothesis"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def esc(s):
    if s is None:
        return ""
    return html_mod.escape(str(s))


def fmt_date(iso):
    try:
        from datetime import datetime
        return datetime.fromisoformat(str(iso)).strftime("%b %d, %Y %I:%M %p")
    except Exception:
        return str(iso)


def set_msg(el, text, kind=""):
    el.text = text or ""
    el.classes("msg", add=kind, remove=("ok" if kind != "ok" else "err", "err" if kind != "err" else "ok"))


# ---------------------------------------------------------------------------
# UI builders
# ---------------------------------------------------------------------------
async def load_status():
    reachable = check_server()
    dot = status_dot
    txt = status_text
    pill = status_pill
    if reachable:
        pill.classes("ok", remove="down")
        dot.classes("dot", remove="")
        txt.text = f"Local LLM online — {LOCAL_MODEL_NAME.split('/')[-1]}"
    else:
        pill.classes("down", remove="ok")
        dot.classes("dot", remove="")
        txt.text = "Local LLM server not reachable — start llama-server on 127.0.0.1:8080"


async def load_entries():
    entries_container.clear()
    try:
        log = mind.read()
    except Exception:
        with entries_container:
            ui.label("Unable to load entries.").classes("empty")
        return
    if log.empty:
        with entries_container:
            ui.label("No reflections yet. Log your first thought below.").classes("empty")
        return
    for _, r in log.iloc[::-1].iterrows():
        with entries_container:
            with ui.element("div").classes("entry"):
                with ui.element("div").classes("entry-meta"):
                    ui.label(esc(r["subject"])).classes("entry-subject")
                    ui.label(fmt_date(r["when"]))
                ui.label(esc(r["observation"])).classes("entry-obs")
                with ui.element("div").classes("entry-tags"):
                    ui.label(esc(r["subject"])).classes("tag")
                    if r["doubt"]:
                        ui.label("doubt").classes("tag")
                    if r["measure"]:
                        ui.label(f"measure: {esc(r['measure'])}").classes("tag")
                    if r["resolved"]:
                        ui.label("resolved").classes("tag")


async def do_reflect():
    obs = observation_input.value.strip()
    if not obs:
        set_msg(form_msg, "Observation cannot be empty.", "err")
        return
    subj = (subject_input.value or "general").strip()
    measure = measure_input.value.strip() or None
    doubt = doubt_input.value.strip() or None
    struggle = struggle_input.value.strip() or None

    reflect_btn.disable()
    reflect_btn.text = "Logging…"
    set_msg(form_msg, "", "")

    try:
        eid = mind.reflect(
            subject=subj,
            observation=f"[{EPISTEMIC_TAG}] {obs}",
            measure=measure,
            doubt=doubt,
            struggle=struggle,
        )
        subject_input.value = ""
        observation_input.value = ""
        measure_input.value = ""
        doubt_input.value = ""
        struggle_input.value = ""
        set_msg(form_msg, f"Logged reflection #{eid}.", "ok")
        await load_entries()
    except Exception as e:
        set_msg(form_msg, f"Failed to log: {e}", "err")
    finally:
        reflect_btn.enable()
        reflect_btn.text = "Log Reflection"


async def do_critique():
    obs = critique_obs.value.strip()
    if not obs:
        critique_out.text = "Enter an observation first."
        critique_out.classes("", remove="error-msg")
        return
    subj = (critique_subj.value or "general").strip()

    critique_btn.disable()
    critique_btn.text = "Asking local LLM…"
    critique_out.text = ""

    if not check_server():
        critique_out.text = "Local LLM server not reachable at http://127.0.0.1:8080"
        critique_btn.enable()
        critique_btn.text = "Get Critique"
        return

    try:
        fb = critique(
            observation=obs,
            subject=subj,
            world_keys=list(mind.world.keys()),
            heat_level=HEAT_LEVEL,
            epistemic_tag=EPISTEMIC_TAG,
        )
        critique_out.text = fb
    except Exception as e:
        critique_out.text = f"Critique failed: {e}"
    finally:
        critique_btn.enable()
        critique_btn.text = "Get Critique"


def set_heat(val):
    global HEAT_LEVEL
    HEAT_LEVEL = val
    for c in heat_chips:
        is_active = c.props.get("data-val") == str(val)
        c.classes("active", add=is_active, remove=not is_active)


def set_tag(tag):
    global EPISTEMIC_TAG
    EPISTEMIC_TAG = tag


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
@ui.page("/")
def index():
    global status_dot, status_text, status_pill
    global subject_input, observation_input, measure_input, doubt_input, struggle_input
    global reflect_btn, form_msg
    global critique_obs, critique_subj, critique_btn, critique_out
    global entries_container, heat_chips

    with ui.column().classes("w-full max-w-5xl mx-auto items-stretch"):
        # Header
        with ui.element("header").classes("w-full mb-4"):
            with ui.row().classes("w-full items-center gap-3 mb-2"):
                ui.label("🧠").classes("text-2xl")
                with ui.column().classes("gap-0"):
                    ui.label("EIGENLOG").classes("glass-title")
                    ui.label("A Python tool to reflect with care. Local. Private.").classes("subtitle")
            status_pill = ui.element("div").classes("ok").props("id=status")
            with status_pill:
                status_dot = ui.element("div").classes("dot").props("id=status-dot")
                status_text = ui.label("Checking local LLM server…").props("id=status-text")

        # Central panel
        with ui.element("section").classes("glass w-full mb-6"):
            with ui.element("div").classes("panel"):
                with ui.grid(columns=2).classes("gap-6 w-full"):
                    for title, sub, extra in [
                        ("KNOW", "Record what you know.", 'code("mind.reflect(subject, observation)")'),
                        ("DOUBT", "Epistemic Tag: Hypothesis — challenge entry? What does not fit?", None),
                    ]:
                        with ui.element("div").classes("card"):
                            ui.label(title).classes("text-xl font-black text-accent mb-1")
                            ui.label(sub).classes("text-sm text-ink-dim")
                            if extra:
                                ui.label(extra).classes("text-xs text-ink mt-2")
                    with ui.element("div").classes("card col-span-2").style("background: rgba(34,197,94,0.08); border-color: rgba(34,197,94,0.25);"):
                        ui.label("PRIVATE & LOCAL").classes("text-xl font-bold text-green-400 mb-1")
                        ui.label("Data Sovereignty\nStrict permissions (0o600)\nSQLite database — encrypted on your disk").classes("text-green-100 text-sm")

        # Main content column
        with ui.row().classes("w-full gap-6 items-start"):
            # Left column: form + critic
            with ui.column().classes("flex-1 gap-6"):
                # Log form
                with ui.element("section").classes("glass w-full"):
                    with ui.element("div").classes("panel"):
                        ui.label("Log a reflection").classes("text-lg font-black mb-4")
                        with ui.grid(columns=2).classes("gap-4 w-full items-end"):
                            subject_input = ui.input("Subject / Domain", placeholder="e.g. emotions, work, code").classes("w-full")
                            with ui.column().classes("col-span-2"):
                                observation_input = ui.textarea("Observation / Thought", placeholder="What's on your mind?").classes("w-full")
                            measure_input = ui.input("Measure / Scale (optional)", placeholder="e.g. 8/10, calm").classes("w-full")
                            doubt_input = ui.input("Doubt / Tension (optional)", placeholder="What's unresolved?").classes("w-full")
                            with ui.column().classes("col-span-2"):
                                ui.label("Epistemic Tag").classes("text-xs font-bold text-ink-dim uppercase tracking-wider mb-1")
                                with ui.row().classes("gap-2 wrap"):
                                    tag_hyp = ui.chip("Hypothesis — open to friction", color="accent").props("data-tag=hypothesis").classes("chip active")
                                    tag_subj = ui.chip("Subjective Truth — shielded", color="accent").props("data-tag=subjective truth").classes("chip")
                                    tag_hyp.on("click", lambda: (set_tag("hypothesis"), tag_hyp.classes("active", add=True, remove=False), tag_subj.classes("active", add=False, remove=True)))
                                    tag_subj.on("click", lambda: (set_tag("subjective truth"), tag_subj.classes("active", add=True, remove=False), tag_hyp.classes("active", add=False, remove=True)))
                                epistemic_hidden = ui.input(value="hypothesis").classes("hidden")
                        reflect_btn = ui.button("Log Reflection", on_click=do_reflect).classes("btn-primary w-full mt-2")
                        form_msg = ui.label("").classes("msg")

                # Critic
                with ui.element("section").classes("glass w-full"):
                    with ui.element("div").classes("panel"):
                        ui.label("Local LLM Critic").classes("text-lg font-black mb-2")
                        ui.label("Powered by your llama-server on 127.0.0.1:8080. Nothing leaves this machine.").classes("text-sm text-ink-dim mb-4")
                        critique_obs = ui.textarea("Observation to critique", placeholder="Paste an observation here…").classes("w-full")
                        critique_subj = ui.input("Subject", placeholder="e.g. emotions").classes("w-full")
                        ui.label("Heat Dial").classes("text-xs font-bold text-ink-dim uppercase tracking-wider mt-4 mb-1")
                        with ui.row().classes("gap-2 wrap w-full"):
                            heat_chips = []
                            for val, label in [(0, "Grammar & Logic"), (1, "Mirror"), (2, "Dialectic"), (3, "Forensic")]:
                                c = ui.chip(label, color="accent").props(f"data-val={val}").classes("chip" + (" active" if val == 2 else ""))
                                heat_chips.append(c)
                                c.on("click", lambda v=val, el=c: (set_heat(v), [hc.classes("active", add=False, remove=True) for hc in heat_chips], el.classes("active", add=True, remove=False)))
                        with ui.row().classes("gap-3 mt-4 wrap"):
                            critique_btn = ui.button("Get Critique", on_click=do_critique).classes("btn-primary")
                            ui.button("Clear", on_click=lambda: (critique_obs.set_value(""), critique_out.set_text(""))).classes("btn-secondary")
                        critique_out = ui.label("").classes("critique-box")

            # Right column: side rail + entries
            with ui.column().classes("w-64 gap-6 shrink-0"):
                for icon, label_txt in [("🦙", "Local LLM"), ("❄️", "Cold Mode"), ("↩️", "Prior entry")]:
                    with ui.element("div").classes("side-card"):
                        ui.label(icon).classes("side-icon")
                        ui.label(label_txt).classes("h3")

                ui.separator().classes("my-4")

                with ui.element("section").classes("glass w-full"):
                    with ui.element("div").classes("panel"):
                        ui.label("Your Log").classes("text-lg font-black mb-4")
                        entries_container = ui.column().classes("w-full gap-2")

        # Footer
        ui.label("Eigenlog — local-first, 0o600 SQLite, no cloud, no telemetry.   |   CODE: github.com/ykhattam/eigenlog").classes("footer")

    # Initial load
    ui.timer(0.5, load_status, once=True)
    ui.timer(0.7, load_entries, once=True)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ in ("__main__", "__nicegui_main__"):
    ui.run(host="127.0.0.1", port=5000, title="Eigenlog", reload=False)
