"""eigenlog web: localhost-only glass-morphism reflection UI.

Privacy: binds strictly to 127.0.0.1, no external CDNs, no telemetry,
no cloud. Reuses PersistentMind (SQLite) and ai_critic (local LLM).
"""
import os
import sys

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
    log = mind.read()
    if log.empty:
        return jsonify([])
    rows = log.to_dict(orient="records")
    out = []
    for r in rows:
        out.append({
            "id": int(r["id"]),
            "when": str(r["when"]),
            "subject": r["subject"],
            "observation": r["observation"],
            "measure": r["measure"] if r["measure"] == r["measure"] else None,
            "doubt": r["doubt"] if r["doubt"] == r["doubt"] else None,
            "struggle": r["struggle"] if r["struggle"] == r["struggle"] else None,
            "resolved": int(r["resolved"]),
        })
    return jsonify(out)


@app.route("/api/reflect", methods=["POST"])
def api_reflect():
    data = request.get_json(force=True) or {}
    subject = (data.get("subject") or "general").strip()
    observation = (data.get("observation") or "").strip()
    if not observation:
        return jsonify({"error": "observation required"}), 400
    eid = mind.reflect(
        subject=subject,
        observation=observation,
        measure=(data.get("measure") or None),
        doubt=(data.get("doubt") or None),
        struggle=(data.get("struggle") or None),
    )
    return jsonify({"id": eid})


@app.route("/api/critique", methods=["POST"])
def api_critique():
    if not check_server():
        return jsonify({"error": "Local LLM server not reachable at http://127.0.0.1:8080"}), 503
    data = request.get_json(force=True) or {}
    fb = critique(
        observation=data.get("observation", ""),
        subject=data.get("subject", "general"),
        world_keys=list(mind.world.keys()),
        heat_level=int(data.get("heat_level", 2)),
        epistemic_tag=data.get("epistemic_tag", "hypothesis"),
    )
    return jsonify({"feedback": fb})


@app.route("/api/server-status")
def api_server_status():
    return jsonify({
        "reachable": check_server(),
        "model": LOCAL_MODEL_NAME,
        "url": "http://127.0.0.1:8080",
    })


if __name__ == "__main__":
    # Loopback only — never expose to the network.
    app.run(host="127.0.0.1", port=5000, debug=False)
