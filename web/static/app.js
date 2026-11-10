// eigenlog web frontend — glass morphism, localhost only
const API = "/api";
let heatLevel = 2;
let epistemicTag = "hypothesis";

// ---------- helpers ----------
function escapeHtml(s) {
  if (s == null) return "";
  const div = document.createElement("div");
  div.textContent = String(s);
  return div.innerHTML;
}

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch (e) {
    return iso;
  }
}

function setMsg(elId, text, kind) {
  const el = document.getElementById(elId);
  if (!el) return;
  el.textContent = text || "";
  el.className = "msg " + (kind || "");
}

// ---------- status ----------
async function loadStatus() {
  try {
    const r = await fetch(`${API}/server-status`, { cache: "no-store" });
    const j = await r.json();
    const dot = document.getElementById("status-dot");
    const txt = document.getElementById("status-text");
    const pill = document.getElementById("status");
    if (j.reachable) {
      pill.className = "ok";
      dot.className = "dot";
      txt.textContent = `Local LLM online — ${j.model.split("/").pop()}`;
    } else {
      pill.className = "down";
      dot.className = "dot";
      txt.textContent = "Local LLM server not reachable — start llama-server on 127.0.0.1:8080";
    }
  } catch (e) {
    const txt = document.getElementById("status-text");
    if (txt) txt.textContent = "Status check failed.";
  }
}

// ---------- entries ----------
async function loadEntries() {
  const container = document.getElementById("entries");
  if (!container) return;
  try {
    const r = await fetch(`${API}/entries`, { cache: "no-store" });
    const entries = await r.json();
    container.innerHTML = "";
    if (!entries || !entries.length) {
      container.innerHTML = `<div class="empty">No reflections yet. Log your first thought below.</div>`;
      return;
    }
    // newest first
    [...entries].reverse().forEach((e) => {
      const card = document.createElement("div");
      card.className = "entry";
      const tags = [
        `<span class="tag">${escapeHtml(e.subject)}</span>`,
        e.doubt ? `<span class="tag">doubt</span>` : "",
        e.measure ? `<span class="tag">measure: ${escapeHtml(e.measure)}</span>` : "",
        e.resolved ? `<span class="tag">resolved</span>` : "",
      ].filter(Boolean).join("");

      card.innerHTML = `
        <div class="entry-meta">
          <span class="entry-subject">${escapeHtml(e.subject)}</span>
          <span>${formatDate(e.when)}</span>
        </div>
        <p class="entry-obs">${escapeHtml(e.observation)}</p>
        <div class="entry-tags">${tags}</div>
        <button class="btn-delete" data-id="${e.id}" title="Delete entry">&times;</button>
      `;
      container.appendChild(card);
    });

    // wire delete buttons
    container.querySelectorAll(".btn-delete").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const id = btn.dataset.id;
        if (!confirm("Delete this reflection?")) return;
        try {
          const r = await fetch(`${API}/entries/${id}`, { method: "DELETE" });
          if (!r.ok) throw new Error("delete failed");
          loadEntries();
        } catch (err) {
          setMsg("quick-msg", "Could not delete entry.", "err");
        }
      });
    });
  } catch (err) {
    container.innerHTML = `<div class="empty">Unable to load entries.</div>`;
    setMsg("quick-msg", "Failed to load entries.", "err");
  }
}

// ---------- submit entry ----------
async function submitEntry(e) {
  e.preventDefault();
  const form = document.getElementById("reflect-form");
  const fd = new FormData(form);
  const data = {
    subject: fd.get("subject") || "",
    observation: fd.get("observation") || "",
    measure: fd.get("measure") || null,
    doubt: fd.get("doubt") || null,
    struggle: fd.get("struggle") || null,
    epistemic_tag: fd.get("epistemic_tag") || "hypothesis",
  };
  const btn = form.querySelector('button[type="submit"]');
  const orig = btn.textContent;
  btn.disabled = true;
  btn.textContent = "Logging…";
  setMsg("quick-msg", "", "");

  try {
    const r = await fetch(`${API}/reflect`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || "failed to log");
    form.reset();
    setMsg("quick-msg", `Logged reflection #${j.id}.`, "ok");
    loadEntries();
  } catch (err) {
    setMsg("quick-msg", err.message, "err");
  } finally {
    btn.disabled = false;
    btn.textContent = orig;
  }
}

// ---------- critique ----------
async function runCritique() {
  const obsEl = document.getElementById("crit-obs");
  const subjEl = document.getElementById("crit-subj");
  const outEl = document.getElementById("crit-out");
  const btn = document.getElementById("crit-btn");
  const obs = (obsEl.value || "").trim();
  const subj = (subjEl.value || "general").trim();
  if (!obs) {
    outEl.textContent = "Enter an observation first.";
    outEl.className = "";
    return;
  }
  btn.disabled = true;
  btn.textContent = "Asking local LLM…";
  outEl.textContent = "";
  outEl.className = "";

  try {
    const r = await fetch(`${API}/critique`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        observation: obs,
        subject: subj,
        heat_level: parseInt(document.getElementById("crit-heat").value, 10) || 2,
        epistemic_tag: epistemicTag,
      }),
    });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || "critique failed");
    outEl.textContent = j.feedback;
  } catch (err) {
    outEl.textContent = err.message;
    outEl.className = "error-msg";
  } finally {
    btn.disabled = false;
    btn.textContent = "Get Critique";
  }
}

// ---------- heat dial ----------
function selectHeat(val) {
  heatLevel = val;
  document.querySelectorAll(".heat-chip").forEach((c) => {
    c.classList.toggle("active", c.dataset.val === String(val));
  });
}

// ---------- epistemic tag ----------
function setEpistemicTag(tag) {
  epistemicTag = tag;
  document.querySelectorAll(".tag-chip").forEach((c) => {
    c.classList.toggle("active", c.dataset.tag === tag);
  });
}

// ---------- init ----------
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("reflect-form");
  if (form) form.addEventListener("submit", submitEntry);

  const critBtn = document.getElementById("crit-btn");
  if (critBtn) critBtn.addEventListener("click", runCritique);

  // heat chips
  document.querySelectorAll(".heat-chip").forEach((c) => {
    c.addEventListener("click", () => selectHeat(c.dataset.val));
  });

  // epistemic chips
  document.querySelectorAll(".tag-chip").forEach((c) => {
    c.addEventListener("click", () => setEpistemicTag(c.dataset.tag));
  });

  loadStatus();
  loadEntries();
  setInterval(loadStatus, 15000);
});
