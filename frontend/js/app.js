/* ─────────────────────────────────────────────────
   CODENAME/GEN — Codename Generation System
   app.js — all client-side logic
───────────────────────────────────────────────── */

const API = 'http://localhost:8000';

/* ── State ── */
let genCount = 3;

const styleNames = {
  military: 'MILITARY',
  nature:   'NATURE',
  abstract: 'ABSTRACT',
  cosmic:   'COSMIC',
};

/* ── Clock ── */
function tick() {
  document.getElementById('topbar-clock').textContent =
    new Date().toLocaleTimeString('en-GB');
}
tick();
setInterval(tick, 1000);

/* ── API ── */
async function apiFetch(path, opts = {}) {
  const res = await fetch(API + path, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (res.status === 204) return null;
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
  return data;
}

/* ── Toast ── */
function toast(msg, type = 'ok') {
  const area = document.getElementById('toast-area');
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = `> ${msg}`;
  area.appendChild(el);
  setTimeout(() => el.remove(), 5000);
}

/* ── Segment controls ── */
function initSegControls() {
  document.querySelectorAll('.seg-control').forEach(ctrl => {
    ctrl.querySelectorAll('.seg-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        ctrl.querySelectorAll('.seg-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        // Update style full name if it's the style seg
        if (ctrl.id === 'seg-style') {
          const name = document.getElementById('style-full-name');
          if (name) name.textContent = styleNames[btn.dataset.val] ?? btn.dataset.val.toUpperCase();
        }
      });
    });
  });
}

function getSegVal(id) {
  const btn = document.querySelector(`#${id} .seg-btn.active`);
  return btn ? btn.dataset.val : null;
}

/* ── Count ── */
function adjustCount(delta) {
  genCount = Math.max(1, Math.min(20, genCount + delta));
  document.getElementById('count-display').textContent = genCount;
}

/* ── Tab switching ── */
function initTabs() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const pane = btn.dataset.pane;
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(`pane-${pane}`).classList.add('active');
      if (pane === 'registry')   loadRegistry();
      if (pane === 'analytics')  loadStyleStats();
      if (pane === 'namespaces') loadNamespaces();
    });
  });
}

/* ── Summary ── */
async function loadSummary() {
  try {
    const d = await apiFetch('/stats/summary');
    document.getElementById('hs-total').textContent   = d.total_generated ?? 0;
    document.getElementById('hs-active').textContent  = d.active          ?? 0;
    document.getElementById('hs-retired').textContent = d.retired         ?? 0;
    document.getElementById('hs-recycled').textContent= d.recycled        ?? 0;
    const badge = document.getElementById('conn-badge');
    badge.textContent = '● ONLINE';
    badge.classList.add('online');
  } catch {
    const badge = document.getElementById('conn-badge');
    badge.textContent = '● OFFLINE';
    badge.classList.remove('online');
  }
}

/* ── Generate ── */
async function generate() {
  const btn  = document.getElementById('gen-btn');
  const strip = document.getElementById('output-strip');
  const ns   = document.getElementById('g-namespace').value.trim() || 'global';
  const assignTo = document.getElementById('g-assign').value.trim() || null;

  const payload = {
    count:       genCount,
    style:       getSegVal('seg-style')  || 'military',
    language:    getSegVal('seg-lang')   || 'en',
    word_count:  parseInt(getSegVal('seg-words') || '2'),
    separator:   getSegVal('seg-sep')    || 'space',
    namespace:   ns,
    assign_to:   assignTo,
  };

  btn.disabled = true;
  btn.querySelector('.gen-btn-text').textContent = 'PROCESSING…';
  strip.innerHTML = `<div class="loading-row"><span class="spinner"></span> Generating…</div>`;

  try {
    const res = await apiFetch('/generate', { method: 'POST', body: JSON.stringify(payload) });

    strip.innerHTML = res.codenames
      .map((name, i) =>
        `<div class="codename-chip" style="animation-delay:${i * 0.06}s" title="Click to copy" onclick="copyName('${name}')">${name}</div>`)
      .join('') +
      `<div class="output-meta">// ${res.generated_count} codename(s) · ns:${res.namespace} · ids:[${res.ids.join(',')}]</div>`;

    toast(`Generated ${res.generated_count} codename(s)`, 'ok');
    loadSummary();
    if (document.getElementById('pane-registry').classList.contains('active')) {
      loadRegistry();
    }
  } catch (err) {
    strip.innerHTML = `<div class="loading-row" style="color:var(--red);">ERROR: ${esc(err.message)}</div>`;
    toast(err.message, 'err');
  } finally {
    btn.disabled = false;
    btn.querySelector('.gen-btn-text').textContent = 'GENERATE';
  }
}

function copyName(name) {
  navigator.clipboard.writeText(name)
    .then(() => toast(`Copied: ${name}`, 'ok'))
    .catch(() => toast('Copy failed', 'err'));
}

/* ── Registry ── */
async function loadRegistry() {
  const body = document.getElementById('registry-body');
  body.innerHTML = `<div class="loading-row"><span class="spinner"></span> Loading registry…</div>`;
  try {
    const items = await apiFetch('/codenames?limit=50');
    if (!items.length) {
      body.innerHTML = '<div class="empty-row">NO RECORDS FOUND</div>';
      return;
    }
    const rows = items.map(c => `
      <tr>
        <td class="cell-name">${esc(c.value)}</td>
        <td><span class="style-pill style-${c.style.toLowerCase()}">${c.style.toUpperCase()}</span></td>
        <td><span class="status-pill status-${c.status.toLowerCase()}">${c.status.toUpperCase()}</span></td>
        <td style="color:var(--dim);font-size:0.7rem;">${c.namespace_id}</td>
        <td style="color:var(--dim);font-size:0.7rem;">${c.assigned_to ?? '—'}</td>
        <td style="color:var(--dim);font-size:0.7rem;">${fmtDate(c.generated_at)}</td>
        <td>${c.status === 'active'
          ? `<button class="btn-retire" onclick="retireOne(${c.id},this)">RETIRE</button>`
          : ''}</td>
      </tr>`).join('');
    body.innerHTML = `
      <table class="registry-table">
        <thead><tr>
          <th>Codename</th><th>Style</th><th>Status</th>
          <th>NS</th><th>Assigned To</th><th>Generated</th><th></th>
        </tr></thead>
        <tbody>${rows}</tbody>
      </table>`;
  } catch (err) {
    body.innerHTML = `<div class="loading-row" style="color:var(--red);">${esc(err.message)}</div>`;
  }
}

async function retireOne(id, btn) {
  btn.textContent = '…';
  btn.disabled = true;
  try {
    await apiFetch(`/codenames/${id}/retire`, {
      method: 'POST',
      body: JSON.stringify({ reason: 'manual' }),
    });
    toast(`Codename #${id} retired`, 'warn');
    loadRegistry();
    loadSummary();
  } catch (err) {
    toast(err.message, 'err');
    btn.textContent = 'RETIRE';
    btn.disabled = false;
  }
}

/* ── Style stats ── */
async function loadStyleStats() {
  const el = document.getElementById('style-chart');
  try {
    const stats = await apiFetch('/stats/styles');
    if (!stats.length) { el.innerHTML = '<div class="empty-row">No data</div>'; return; }
    const max = Math.max(...stats.map(s => s.total_generated), 1);
    const colors = { military: '#e67e22', nature: '#27ae60', abstract: '#5dade2', cosmic: '#a569bd' };
    el.innerHTML = `<div class="style-bars">${
      stats.map(s => `
        <div class="sbar-row">
          <div class="sbar-label">
            <span style="color:${colors[s.style] ?? 'var(--white)'}">${s.style.toUpperCase()}</span>
            <span style="color:var(--dim)">${s.total_generated} &nbsp;·&nbsp; ${s.pct_of_total}%</span>
          </div>
          <div class="sbar-track">
            <div class="sbar-fill" style="width:${(s.total_generated/max*100).toFixed(1)}%;background:${colors[s.style] ?? 'var(--red)'}"></div>
          </div>
        </div>`).join('')
    }</div>`;
  } catch (err) {
    el.innerHTML = `<div class="loading-row" style="color:var(--red);">${esc(err.message)}</div>`;
  }
}

/* ── Saturation ── */
async function loadSaturation() {
  const ns    = document.getElementById('sat-ns-input').value.trim() || 'global';
  const style = document.getElementById('sat-style-input').value;
  const el    = document.getElementById('sat-display');
  el.innerHTML = `<span class="spinner"></span>`;
  try {
    const d   = await apiFetch(`/namespaces/${ns}/saturation?style=${style}&word_count=2`);
    const pct = Math.min(d.saturation_pct, 100);
    const R   = 40;
    const circ = 2 * Math.PI * R;
    const dash = (pct / 100) * circ;
    const color = pct > 80 ? 'var(--red)' : pct > 50 ? '#d4a017' : '#27ae60';
    el.innerHTML = `
      <div class="sat-ring-wrap">
        <div class="sat-ring">
          <svg width="90" height="90" viewBox="0 0 90 90">
            <circle cx="45" cy="45" r="${R}" fill="none" stroke="rgba(242,240,235,0.07)" stroke-width="5"/>
            <circle cx="45" cy="45" r="${R}" fill="none" stroke="${color}" stroke-width="5"
              stroke-dasharray="${dash.toFixed(2)} ${circ.toFixed(2)}"
              stroke-linecap="square"
              style="filter:drop-shadow(0 0 4px ${color})"/>
          </svg>
          <div class="sat-ring-label" style="color:${color}">${pct.toFixed(0)}%</div>
        </div>
        <div class="sat-info">
          Pool size: <strong>${d.pool_size.toLocaleString()}</strong><br>
          Active: <strong>${d.active_count}</strong><br>
          Remaining: <strong style="color:${color}">${d.estimated_remaining.toLocaleString()}</strong><br>
          Namespace: <strong>${esc(d.namespace)}</strong>
        </div>
      </div>`;
  } catch (err) {
    el.innerHTML = `<span style="color:var(--red);font-size:0.72rem;">ERROR: ${esc(err.message)}</span>`;
  }
}

/* ── Namespaces ── */
async function loadNamespaces() {
  const body = document.getElementById('ns-body');
  body.innerHTML = `<div class="loading-row"><span class="spinner"></span> Loading…</div>`;
  try {
    const list = await apiFetch('/namespaces');
    if (!list.length) { body.innerHTML = '<div class="empty-row">NO NAMESPACES</div>'; return; }
    const rows = list.map(n => `
      <tr>
        <td class="ns-slug">${esc(n.slug)}</td>
        <td style="color:var(--dim);font-size:0.72rem;">${esc(n.description ?? '—')}</td>
        <td style="color:var(--dim);font-size:0.72rem;">${esc(n.owner ?? '—')}</td>
        <td style="font-family:Oswald,sans-serif;font-size:1rem;font-weight:600;">${n.codename_count}</td>
        <td style="color:var(--dim);font-size:0.7rem;">${fmtDate(n.created_at)}</td>
      </tr>`).join('');
    body.innerHTML = `
      <table class="ns-table">
        <thead><tr><th>Slug</th><th>Description</th><th>Owner</th><th>Codenames</th><th>Created</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>`;
  } catch (err) {
    body.innerHTML = `<div class="loading-row" style="color:var(--red);">${esc(err.message)}</div>`;
  }
}

async function createNamespace() {
  const slug = document.getElementById('ns-slug-input').value.trim();
  if (!slug) { toast('Slug is required', 'err'); return; }
  try {
    const ns = await apiFetch('/namespaces', {
      method: 'POST',
      body: JSON.stringify({
        slug,
        description: document.getElementById('ns-desc-input').value.trim() || null,
      }),
    });
    toast(`Namespace '${ns.slug}' created`, 'ok');
    document.getElementById('ns-slug-input').value = '';
    document.getElementById('ns-desc-input').value = '';
    loadNamespaces();
  } catch (err) {
    toast(err.message, 'err');
  }
}

/* ── Helpers ── */
function esc(s = '') {
  return String(s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function fmtDate(iso) {
  return new Date(iso).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

/* ── Boot ── */
initSegControls();
initTabs();
loadSummary();
loadRegistry();
