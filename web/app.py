"""eigenlog web — localhost-only glass-morphism reflection UI.

Privacy: binds strictly to 127.0.0.1, no external CDNs, no telemetry,
no cloud. Reuses PersistentMind (SQLite) and ai_critic (local LLM).
"""
import os
import sys
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from flask import Flask, render_template, request, jsonify
from interactive_mind import PersistentMind
from ai_critic import critique, check_server, LOCAL_MODEL_NAME

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "static"),
)

DB_PATH = os.path.join(ROOT, "eigenlog.db")
mind = PersistentMind(db_path=DB_PATH)

MAX_OBS_LEN = 4000
MAX_SUBJECT_LEN = 100
MAX_MEASURE_LEN = 50


def _sanitize_text(value, max_len):
    """Strip HTML and enforce length limits."""
    import html as html_mod
    if value is None:
        return None
    text = html_mod.escape(str(value).strip())
    if len(text) > max_len:
        text = text[:max_len]
    return text or None


@app.route("/")
def index():
    cfg = {"mode": "2", "heat_level": 2}
    try:
        import json
        cfg_path = os.path.join(ROOT, ".eigenlog_config")
        if os.path.exists(cfg_path):
            with open(cfg_path) as f:
                cfg = json.load(f)
    except Exception:
        pass
    return render_template("index.html", config=cfg)


@app.route("/api/entries")
def api_entries():
    try:
        log = mind.read()
    except Exception as e:
        return jsonify({"error": f"database read failed: {e}"}), 500
    if log.empty:
        return jsonify([])
    rows = log.to_dict(orient="records")
    out = []
    for r in rows:
        out.append({
            "id": int(r["id"]),
            "when": str(r["when"]),
            "subject": r["subject"] or "general",
            "observation": r["observation"] or "",
            "measure": r["measure"] if r["measure"] == r["measure"] else None,
            "doubt": r["doubt"] if r["doubt"] == r["doubt"] else None,
            "struggle": r["struggle"] if r["struggle"] == r["struggle"] else None,
            "resolved": int(r["resolved"]),
        })
    return jsonify(out)


@app.route("/api/reflect", methods=["POST"])
def api_reflect():
    data = request.get_json(force=True, silent=True) or {}
    subject = _sanitize_text(data.get("subject"), MAX_SUBJECT_LEN) or "general"
    observation = _sanitize_text(data.get("observation"), MAX_OBS_LEN)
    if not observation:
        return jsonify({"error": "observation is required"}), 400
    measure = _sanitize_text(data.get("measure"), MAX_MEASURE_LEN)
    doubt = _sanitize_text(data.get("doubt"), MAX_OBS_LEN)
    struggle = _sanitize_text(data.get("struggle"), MAX_OBS_LEN)
    epistemic_tag = data.get("epistemic_tag", "hypothesis")
    if epistemic_tag not in ("hypothesis", "subjective truth"):
        epistemic_tag = "hypothesis"

    try:
        eid = mind.reflect(
            subject=subject,
            observation=f"[{epistemic_tag}] {observation}",
            measure=measure,
            doubt=doubt,
            struggle=struggle,
        )
    except Exception as e:
        return jsonify({"error": f"database write failed: {e}"}), 500

    return jsonify({"id": eid})


@app.route("/api/entries/<int:entry_id>", methods=["DELETE"])
def api_delete_entry(entry_id):
    try:
        import sqlite3
        c = sqlite3.connect(mind.db_path)
        cur = c.execute("SELECT id FROM entries WHERE id=?", (entry_id,))
        if not cur.fetchone():
            c.close()
            return jsonify({"error": "entry not found"}), 404
        c.execute("DELETE FROM entries WHERE id=?", (entry_id,))
        c.commit()
        c.close()
    except Exception as e:
        return jsonify({"error": f"delete failed: {e}"}), 500
    return jsonify({"ok": True})


@app.route("/api/critique", methods=["POST"])
def api_critique():
    if not check_server():
        return jsonify({"error": "Local LLM server not reachable at http://127.0.0.1:8080"}), 503
    data = request.get_json(force=True, silent=True) or {}
    observation = _sanitize_text(data.get("observation"), MAX_OBS_LEN) or ""
    subject = _sanitize_text(data.get("subject"), MAX_SUBJECT_LEN) or "general"
    try:
        heat_level = int(data.get("heat_level", 2))
    except (TypeError, ValueError):
        heat_level = 2
    heat_level = max(0, min(3, heat_level))
    epistemic_tag = data.get("epistemic_tag", "hypothesis")
    if epistemic_tag not in ("hypothesis", "subjective truth"):
        epistemic_tag = "hypothesis"

    try:
        fb = critique(
            observation=observation,
            subject=subject,
            world_keys=list(mind.world.keys()),
            heat_level=heat_level,
            epistemic_tag=epistemic_tag,
        )
    except Exception as e:
        return jsonify({"error": f"critique failed: {e}"}), 500
    return jsonify({"feedback": fb})


@app.route("/api/server-status")
def api_server_status():
    return jsonify({
        "reachable": check_server(),
        "model": LOCAL_MODEL_NAME,
        "url": "http://127.0.0.1:8080",
    })


@app.errorhandler(400)
def _bad_request(e):
    return jsonify({"error": str(e.description or "bad request")}), 400


@app.errorhandler(500)
def _server_error(e):
    return jsonify({"error": "internal server error"}), 500


if __name__ == "__main__":
    # Loopback only — never expose to the network.
    app.run(host="127.0.0.1", port=5000, debug=False)
