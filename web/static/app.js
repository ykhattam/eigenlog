// eigenlog web frontend — glass morphism, localhost only
const API = "/api";
let heatLevel = 2;

async function loadStatus() {
  try {
    const r = await fetch(`${API}/server-status`);
    const j = await r.json();
    const el = document.getElementById("status");
    const dot = document.getElementById("status-dot");
    const txt = document.getElementById("status-text");
    if (j.reachable) {
      el.className = "ok";
      txt.textContent = `Local LLM server online — ${j.model.split("/").pop()}`;
    } else {
      el.className = "down";
      txt.textContent = "Local LLM server not reachable (start llama-server on 127.0.0.1:8080)";
    }
  } catch (e) {
    document.getElementById("status-text").textContent = "Status check failed.";
  }
}

async function loadEntries() {
  const r = await fetch(`${API}/entries`);
  const entries = await r.json();
  const container = document.getElementById("entries");
  container.innerHTML = "";
  if (!entries.length) {
    container.innerHTML = `<div class="empty">No reflections yet. Log your first thought below.</div>`;
    return;
  }
  entries.forEach(e => {
    const card = document.createElement("div");
    card.className = "card";
    const tags = [
      `<span class="tag">${escapeHtml(e.subject)}</span>`,
      e.doubt ? `<span class="tag">doubt</span>` : "",
      e.measure ? `<span class="tag">measure: ${escapeHtml(e.measure)}</span>` : "",
      e.resolved ? `<span class="tag">resolved</span>` : "",
    ].filter(Boolean).join("");

    card.innerHTML = `
      <div class="entry-meta">
        <span class="entry-subject">${escapeHtml(e.subject)}</span>
        <span>${new Date(e.when).toLocaleString()}</span>
      </div>
      <p class="entry-obs">${escapeHtml(e.observation)}</p>
      <div class="entry-tags">${tags}</div>
    `;
    container.appendChild(card);
  });
}

async function submitEntry(e) {
  e.preventDefault();
  const form = document.getElementById("reflect-form");
  const data = {
    subject: form.subject.value,
    observation: form.observation.value,
    measure: form.measure.value || null,
    doubt: form.doubt.value || null,
    struggle: form.struggle.value || null,
    epistemic_tag: form.epistemic_tag.value,
  };
  const btn = form.querySelector("button[type='submit']");
  btn.disabled = true;
  btn.textContent = "Logging…";

  try {
    const r = await fetch(`${API}/reflect`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data),
    });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || "failed");
    form.reset();
    document.getElementById("quick-msg").textContent = `Logged reflection #${j.id}.`;
    document.getElementById("quick-msg").className = "ok-msg";
    loadEntries();
  } catch (err) {
    document.getElementById("quick-msg").textContent = err.message;
    document.getElementById("quick-msg").className = "error-msg";
  } finally {
    btn.disabled = false;
    btn.textContent = "Log Reflection";
  }
}

async function runCritique() {
  const obs = document.getElementById("crit-obs").value.trim();
  const subj = document.getElementById("crit-subj").value.trim() || "general";
  const heat = document.getElementById("crit-heat").value;
  const out = document.getElementById("crit-out");
  const btn = document.getElementById("crit-btn");
  if (!obs) { out.textContent = "Enter an observation first."; return; }
  btn.disabled = true;
  btn.textContent = "Asking local LLM…";
  out.textContent = "";
  out.className = "";

  try {
    const r = await fetch(`${API}/critique`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ observation: obs, subject: subj, heat_level: parseInt(heat), epistemic_tag: "hypothesis" }),
    });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || "critique failed");
    out.textContent = j.feedback;
  } catch (err) {
    out.textContent = err.message;
    out.className = "error-msg";
  } finally {
    btn.disabled = false;
    btn.textContent = "Get Critique";
  }
}

function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}

function selectHeat(val) {
  heatLevel = val;
  document.querySelectorAll(".heat-chip").forEach(c => {
    c.classList.toggle("active", c.dataset.val === val);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  loadStatus();
  loadEntries();
  document.getElementById("reflect-form").addEventListener("submit", submitEntry);
  document.getElementById("crit-btn").addEventListener("click", runCritique);
  document.querySelectorAll(".heat-chip").forEach(c => {
    c.addEventListener("click", () => selectHeat(c.dataset.val));
  });
  setInterval(loadStatus, 15000);
});
