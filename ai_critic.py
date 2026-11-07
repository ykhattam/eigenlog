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
            {"role": "system", "content": "You are a concise cognitive critic."},
            {"role": "user", "content": f"Critique briefly (1 sentence): [{subject}] {observation}"}
        ],
        "temperature": 0.5,
        "max_tokens": 50
    }
    try:
        r = requests.post(LMS_URL, json=payload, timeout=2)
        if r.status_code == 200:
            data = r.json()
            return data["choices"][0]["message"]["content"].strip()
        else:
            return f"[LLM Error: HTTP {r.status_code}]"
    except Exception as e:
        return f"[LLM Request Failed: {e}]"
