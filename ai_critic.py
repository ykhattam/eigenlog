"""ai_critic.py: Optional local LLM critic using Qwen 2.5 Coder via llama-server.
Connects to http://127.0.0.1:8080/v1 if enabled by the user.
"""
import os
import requests

LMS_URL = os.getenv("LMS_URL", "http://127.0.0.1:8080/v1/chat/completions")

def check_server():
    try:
        res = requests.get("http://127.0.0.1:8080/health", timeout=1)
        return res.status_code == 200
    except Exception:
        return False

def critique(observation, subject="general"):
    if not check_server():
        return "[Local LLM server not reachable at http://127.0.0.1:8080]"
    
    payload = {
        "model": "qwen2.5-coder",
        "messages": [
            {"role": "system", "content": "You are a rigorous philosophical and cognitive critic reviewing a personal eigenlog entry. Be concise, precise, and constructively critical."},
            {"role": "user", "content": f"Subject: {subject}\nObservation: {observation}\n\nCritique this reflection for logical consistency, potential blind spots, or deeper questions."}
        ],
        "temperature": 0.7,
        "max_tokens": 250
    }
    try:
        r = requests.post(LMS_URL, json=payload, timeout=5)
        if r.status_code == 200:
            data = r.json()
            return data["choices"][0]["message"]["content"].strip()
        else:
            return f"[LLM Error: HTTP {r.status_code}]"
    except Exception as e:
        return f"[LLM Request Failed: {e}]"
