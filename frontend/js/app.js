/**
 * app.js — AI ATS Single Page Application
 * Handles routing, state management, and all page logic.
 */

'use strict';

// ─────────────────────────────────────────────
// SESSION STATE
// ─────────────────────────────────────────────
const state = {
  totalProcessed: 0,
  scores: [],
  categories: [],
  screeningHistory: [],   // [{fileName, category, confidence}]
  rankingHistory: [],     // [{topCandidate, topScore, candidates}]
};

// ─────────────────────────────────────────────
// ROUTER
// ─────────────────────────────────────────────
const PAGES = ['dashboard', 'screening', 'ranking', 'analytics'];

function getPage() {
  const hash = location.hash.replace('#', '').trim();
  return PAGES.includes(hash) ? hash : 'dashboard';
}

function navigateTo(page) {
  location.hash = page;
}

function renderPage(page) {
  PAGES.forEach(p => {
    const el = document.getElementById(`page-${p}`);
    const nav = document.getElementById(`nav-${p}`);
    if (el)  el.classList.toggle('hidden', p !== page);
    if (nav) nav.classList.toggle('active', p === page);
  });

  // Refresh data-driven pages
  if (page === 'dashboard')  renderDashboard();
  if (page === 'analytics')  renderAnalytics();
}

window.addEventListener('hashchange', () => renderPage(getPage()));

// ─────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────
function tier(pct) {
  if (pct >= 75) return 'em';
  if (pct >= 50) return 'am';
  return 'sl';
}

function tierLabel(pct) {
  if (pct >= 85) return 'Excellent';
  if (pct >= 75) return 'Strong';
  if (pct >= 60) return 'Moderate';
  if (pct >= 40) return 'Fair';
  return 'Low';
}

function makeGauge(pct, size = 76) {
  const r = 30;
  const circ = 188.5;
  const offset = circ * (1 - pct / 100);
  const t = tier(pct);
  return `
    <div class="gauge-wrap" style="width:${size}px;height:${size}px;">
      <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
        <circle class="g-bg" cx="${size/2}" cy="${size/2}" r="${r}"
                stroke-dasharray="${circ}" stroke-dashoffset="0"/>
        <circle class="g-fill g-${t}" cx="${size/2}" cy="${size/2}" r="${r}"
                stroke-dasharray="${circ}" stroke-dashoffset="${offset}"/>
      </svg>
      <div class="gauge-label">${Math.round(pct)}%</div>
    </div>`;
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// ─────────────────────────────────────────────
// API STATUS POLLING
// ─────────────────────────────────────────────
const statusDot  = document.getElementById('status-dot');
const statusText = document.getElementById('api-status-text');

async function pollApiStatus() {
  const ok = await checkApiHealth();
  statusDot.className = `status-dot ${ok ? 'online' : 'offline'}`;
  statusText.textContent = ok ? 'API Online' : 'API Offline';
}

pollApiStatus();
setInterval(pollApiStatus, 8000);

// ─────────────────────────────────────────────
// SIDEBAR / HAMBURGER (mobile)
// ─────────────────────────────────────────────
const sidebar  = document.getElementById('sidebar');
const hamburger = document.getElementById('hamburger');
const overlay  = document.getElementById('sidebar-overlay');

hamburger.addEventListener('click', () => {
  sidebar.classList.toggle('open');
  overlay.classList.toggle('visible');
});
overlay.addEventListener('click', () => {
  sidebar.classList.remove('open');
  overlay.classList.remove('visible');
});

// Close sidebar on nav click (mobile)
document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', () => {
    if (window.innerWidth <= 768) {
      sidebar.classList.remove('open');
      overlay.classList.remove('visible');
    }
  });
});

// ─────────────────────────────────────────────
// PAGE: DASHBOARD
// ─────────────────────────────────────────────
function renderDashboard() {
  const avg = state.scores.length
    ? (state.scores.reduce((a, b) => a + b, 0) / state.scores.length).toFixed(1)
    : 0;

  const uniqueCats = new Set(state.categories).size;

  const topCat = state.categories.length
    ? state.categories.sort((a, b) =>
        state.categories.filter(v => v === b).length -
        state.categories.filter(v => v === a).length)[0]
    : '—';

  document.getElementById('kpi-avg').textContent       = `${avg}%`;
  document.getElementById('kpi-total').textContent     = state.totalProcessed;
  document.getElementById('kpi-diversity').textContent = uniqueCats;
  document.getElementById('kpi-top-cat').textContent   = topCat;

  // Recent activity
  const actSection = document.getElementById('activity-section');
  const actList    = document.getElementById('activity-list');
  const hasActivity = state.rankingHistory.length || state.screeningHistory.length;
  actSection.style.display = hasActivity ? 'block' : 'none';

  if (hasActivity) {
    const items = [];
    [...state.rankingHistory].slice(-3).reverse().forEach(e => {
      const t = tier(e.topScore);
      items.push(`
        <div class="history-item">
          <div>
            <span style="font-weight:700;">🏆 ${escHtml(e.topCandidate)}</span>
            <span class="pill pill-${t}" style="margin-left:8px;">${e.topScore}%</span>
          </div>
          <span style="color:var(--t3);font-size:11px;">${e.candidates} candidate${e.candidates > 1 ? 's' : ''}</span>
        </div>`);
    });
    [...state.screeningHistory].slice(-5).reverse().forEach(e => {
      const t = tier(e.confidence);
      items.push(`
        <div class="history-item">
          <div>
            <span style="font-weight:600;">📄 ${escHtml(e.fileName)}</span>
            <span style="color:var(--t3);margin:0 6px;">→</span>
            <span class="pill pill-co">${escHtml(e.category)}</span>
          </div>
          <span class="pill pill-${t}">${e.confidence}%</span>
        </div>`);
    });
    actList.innerHTML = items.join('');
  }
}

// ─────────────────────────────────────────────
// PAGE: RESUME SCREENING
// ─────────────────────────────────────────────
let singleFile = null;

const singleInput    = document.getElementById('single-file-input');
const singleFileInfo = document.getElementById('single-file-info');
const singleActionRow = document.getElementById('single-action-row');
const singleSpinner  = document.getElementById('single-spinner');
const singleResult   = document.getElementById('single-result');
const singleDropZone = document.getElementById('single-drop-zone');

function setSingleFile(file) {
  if (!file || !file.name.toLowerCase().endsWith('.pdf')) {
    showAlert(singleResult, 'Only PDF files are supported.', 'err');
    singleResult.classList.remove('hidden');
    return;
  }
  singleFile = file;
  singleFileInfo.innerHTML = `📎 &nbsp;<strong>${escHtml(file.name)}</strong>
    <span style="color:var(--t3);margin-left:8px;">(${formatBytes(file.size)})</span>`;
  singleFileInfo.classList.remove('hidden');
  singleActionRow.style.display = 'flex';
  singleResult.classList.add('hidden');
  singleResult.innerHTML = '';
}

singleInput.addEventListener('change', () => { if (singleInput.files[0]) setSingleFile(singleInput.files[0]); });

// Drag & drop — single
singleDropZone.addEventListener('dragover', e => { e.preventDefault(); singleDropZone.classList.add('drag-over'); });
singleDropZone.addEventListener('dragleave', () => singleDropZone.classList.remove('drag-over'));
singleDropZone.addEventListener('drop', e => {
  e.preventDefault();
  singleDropZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) setSingleFile(file);
});
singleDropZone.addEventListener('click', () => singleInput.click());

// Analyze button
document.getElementById('single-analyze-btn').addEventListener('click', async () => {
  if (!singleFile) return;
  singleSpinner.classList.remove('hidden');
  singleResult.classList.add('hidden');
  singleResult.innerHTML = '';

  const res = await predictResume(singleFile);
  singleSpinner.classList.add('hidden');

  if (res.error) {
    showAlert(singleResult, res.error, 'err');
  } else {
    const cp  = +(res.confidence * 100).toFixed(1);
    const t   = tier(cp);
    const lbl = tierLabel(cp);
    const g   = makeGauge(cp);
    singleResult.innerHTML = `
      <div class="alert alert-ok">✅ &nbsp;Analysis complete — <strong>${escHtml(singleFile.name)}</strong> classified successfully.</div>
      <div class="result-card">
        <div class="rc-top">
          ${g}
          <div class="rc-info">
            <div class="rc-label">Predicted Job Category</div>
            <div class="rc-category">${escHtml(res.predicted_category)}</div>
            <div style="margin-top:12px;display:flex;align-items:center;gap:10px;">
              <span class="pill pill-lg pill-${t}">${cp}% Match</span>
              <span style="color:var(--t3);font-size:12px;">${lbl} confidence</span>
            </div>
          </div>
        </div>
      </div>
      <div class="result-card" style="padding:18px 24px;margin-top:0;">
        <div class="rc-label">Confidence Breakdown</div>
        <div class="bar-outer"><div class="bar-inner bar-${t}" style="width:${cp}%;"></div></div>
        <div style="margin-top:14px;padding-top:14px;border-top:1px solid var(--bdr);">
          <span style="color:var(--t3);font-size:12px;line-height:1.6;">
            <span class="pill pill-la" style="margin-right:6px;">AI</span>
            NLP feature extraction + XGBoost classification determined the most likely job category.
          </span>
        </div>
      </div>`;

    // Update state
    state.totalProcessed++;
    state.scores.push(cp);
    state.categories.push(res.predicted_category);
    state.screeningHistory.push({ fileName: singleFile.name, category: res.predicted_category, confidence: cp });
    renderScreeningHistory();
    renderDashboard();
  }

  singleResult.classList.remove('hidden');
});

// Clear button
document.getElementById('single-clear-btn').addEventListener('click', () => {
  singleFile = null;
  singleInput.value = '';
  singleFileInfo.classList.add('hidden');
  singleActionRow.style.display = 'none';
  singleResult.classList.add('hidden');
  singleResult.innerHTML = '';
});

function renderScreeningHistory() {
  const section = document.getElementById('screening-history-section');
  const list    = document.getElementById('screening-history-list');
  if (!state.screeningHistory.length) { section.style.display = 'none'; return; }
  section.style.display = 'block';
  list.innerHTML = [...state.screeningHistory].slice(-5).reverse().map((e, i) => {
    const t = tier(e.confidence);
    return `<div class="history-item" style="animation-delay:${i * 0.05}s;">
      <div>
        <span style="font-weight:600;">${escHtml(e.fileName)}</span>
        <span style="color:var(--t3);margin:0 6px;">→</span>
        <span class="pill pill-co">${escHtml(e.category)}</span>
      </div>
      <span class="pill pill-${t}">${e.confidence}% Match</span>
    </div>`;
  }).join('');
}

// ─────────────────────────────────────────────
// PAGE: RESUME RANKING
// ─────────────────────────────────────────────
let multiFiles = [];

const multiInput    = document.getElementById('multi-file-input');
const multiFileInfo = document.getElementById('multi-file-info');
const rankRunBtn    = document.getElementById('rank-run-btn');
const rankSpinner   = document.getElementById('rank-spinner');
const rankResult    = document.getElementById('rank-result');
const multiDropZone = document.getElementById('multi-drop-zone');
const jdInput       = document.getElementById('jd-input');

function updateRankBtn() {
  const hasJd    = jdInput.value.trim().length > 0;
  const hasFiles = multiFiles.length > 0;
  rankRunBtn.disabled = !(hasJd && hasFiles);
}

function setMultiFiles(files) {
  const pdfs = Array.from(files).filter(f => f.name.toLowerCase().endsWith('.pdf'));
  if (!pdfs.length) {
    showAlert(rankResult, 'No valid PDF files selected.', 'err');
    rankResult.classList.remove('hidden');
    return;
  }
  multiFiles = pdfs;
  const names = pdfs.slice(0, 3).map(f => escHtml(f.name)).join(', ') + (pdfs.length > 3 ? '…' : '');
  multiFileInfo.innerHTML = `📎 &nbsp;<strong>${pdfs.length} file${pdfs.length > 1 ? 's' : ''}</strong> — <span style="color:var(--t3);">${names}</span>`;
  multiFileInfo.classList.remove('hidden');
  updateRankBtn();
}

multiInput.addEventListener('change', () => { if (multiInput.files.length) setMultiFiles(multiInput.files); });
jdInput.addEventListener('input', updateRankBtn);

// Drag & drop — multi
multiDropZone.addEventListener('dragover', e => { e.preventDefault(); multiDropZone.classList.add('drag-over'); });
multiDropZone.addEventListener('dragleave', () => multiDropZone.classList.remove('drag-over'));
multiDropZone.addEventListener('drop', e => {
  e.preventDefault();
  multiDropZone.classList.remove('drag-over');
  if (e.dataTransfer.files.length) setMultiFiles(e.dataTransfer.files);
});
multiDropZone.addEventListener('click', () => multiInput.click());

// Run ranking
rankRunBtn.addEventListener('click', async () => {
  const jd = jdInput.value.trim();
  if (!jd || !multiFiles.length) return;

  rankSpinner.classList.remove('hidden');
  rankResult.classList.add('hidden');
  rankResult.innerHTML = '';
  rankRunBtn.disabled = true;

  const res = await rankResumes(jd, multiFiles);
  rankSpinner.classList.add('hidden');
  rankRunBtn.disabled = false;

  if (res.error) {
    showAlert(rankResult, res.error, 'err');
  } else {
    const ranking = res.ranking || [];
    if (!ranking.length) {
      showAlert(rankResult, 'No valid resumes could be processed.', 'err');
    } else {
      const medals = ['🥇', '🥈', '🥉'];
      const rows = ranking.map((c, idx) => {
        const rn  = idx + 1;
        const rcls = rn <= 3 ? `rank-${rn}` : 'rank-n';
        const ts  = tier(c.final_score);
        const tc  = tier(c.classification_confidence);
        const d   = (idx * 0.06).toFixed(2);
        return `
          <div class="rank-card" style="animation-delay:${d}s;">
            <div class="rank-badge ${rcls}">#${rn}</div>
            <div class="rank-name">${medals[idx] || ''} ${escHtml(c.file_name)}</div>
            <span class="pill pill-lg pill-${ts}">${c.final_score}%</span>
            <div class="rank-bar-wrap"><div class="rank-bar-fill" style="width:${c.final_score}%;animation-delay:${(parseFloat(d)+0.2).toFixed(2)}s;"></div></div>
            <div class="rank-detail"><span>${c.similarity}%</span>Similarity</div>
            <div class="rank-detail"><span class="pill pill-${tc}" style="font-size:11px;">${c.classification_confidence}%</span><span style="font-size:11px;color:var(--t3);">Confidence</span></div>
            <div class="rank-detail"><span>${c.experience_years}y</span>Exp</div>
          </div>`;
      }).join('');

      rankResult.innerHTML = `
        <div class="alert alert-ok">✅ &nbsp;Ranking complete — <strong>${ranking.length} candidates</strong> analyzed.</div>
        ${rows}
        <div class="divider"></div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
          <button class="btn btn-green" id="csv-download-btn">📥 Download CSV</button>
        </div>
        <details style="margin-top:12px;">
          <summary style="cursor:pointer;font-weight:600;font-size:13px;color:var(--t2);padding:10px 0;">📋 Detailed Results Table</summary>
          <div style="overflow-x:auto;margin-top:10px;">${buildTable(ranking)}</div>
        </details>`;

      // CSV download
      document.getElementById('csv-download-btn').addEventListener('click', () => downloadCsv(ranking));

      // Update state
      state.totalProcessed += ranking.length;
      ranking.forEach(r => state.scores.push(r.final_score));
      state.rankingHistory.push({
        topCandidate: ranking[0].file_name,
        topScore: ranking[0].final_score,
        candidates: ranking.length,
      });
      renderDashboard();
    }
  }

  rankResult.classList.remove('hidden');
});

// Clear ranking
document.getElementById('rank-clear-btn').addEventListener('click', () => {
  multiFiles = [];
  multiInput.value = '';
  multiFileInfo.classList.add('hidden');
  jdInput.value = '';
  rankResult.classList.add('hidden');
  rankResult.innerHTML = '';
  updateRankBtn();
});

function buildTable(ranking) {
  const headers = ['Rank', 'File', 'Final Score', 'Similarity', 'Confidence', 'Experience (yrs)'];
  const ths = headers.map(h => `<th style="text-align:left;padding:8px 12px;background:var(--bg2);font-size:12px;color:var(--t2);font-weight:600;">${h}</th>`).join('');
  const trs = ranking.map((c, i) => `
    <tr style="border-bottom:1px solid var(--bdr);">
      <td style="padding:8px 12px;">${i + 1}</td>
      <td style="padding:8px 12px;">${escHtml(c.file_name)}</td>
      <td style="padding:8px 12px;font-weight:700;">${c.final_score}%</td>
      <td style="padding:8px 12px;">${c.similarity}%</td>
      <td style="padding:8px 12px;">${c.classification_confidence}%</td>
      <td style="padding:8px 12px;">${c.experience_years}</td>
    </tr>`).join('');
  return `<table style="width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden;font-size:13px;">
    <thead><tr>${ths}</tr></thead>
    <tbody>${trs}</tbody>
  </table>`;
}

function downloadCsv(ranking) {
  const headers = ['rank', 'file_name', 'final_score', 'similarity', 'classification_confidence', 'experience_years'];
  const rows = ranking.map((c, i) =>
    [i + 1, `"${c.file_name}"`, c.final_score, c.similarity, c.classification_confidence, c.experience_years].join(',')
  );
  const csv = [headers.join(','), ...rows].join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href = url;
  a.download = 'ai_resume_rankings.csv';
  a.click();
  URL.revokeObjectURL(url);
}

// ─────────────────────────────────────────────
// PAGE: ANALYTICS
// ─────────────────────────────────────────────
function renderAnalytics() {
  const empty   = document.getElementById('analytics-empty');
  const content = document.getElementById('analytics-content');

  if (state.totalProcessed === 0) {
    empty.style.display   = 'block';
    content.style.display = 'none';
    return;
  }
  empty.style.display   = 'none';
  content.style.display = 'block';

  const avg = state.scores.length
    ? (state.scores.reduce((a, b) => a + b, 0) / state.scores.length).toFixed(1)
    : 0;
  const uniqueCats = new Set(state.categories).size;

  document.getElementById('an-total').textContent = state.totalProcessed;
  document.getElementById('an-avg').textContent   = `${avg}%`;
  document.getElementById('an-cats').textContent  = uniqueCats;

  // Score distribution chart
  const chartWrap = document.getElementById('score-chart-wrap');
  const scoreBars = document.getElementById('score-bars');
  if (state.scores.length) {
    chartWrap.style.display = 'block';
    const max = Math.max(...state.scores);
    scoreBars.innerHTML = state.scores.map(s => {
      const h = Math.max(4, Math.round((s / max) * 110));
      return `<div class="bar-chart-col" style="height:${h}px;" title="${s}%"></div>`;
    }).join('');
  } else {
    chartWrap.style.display = 'none';
  }

  // Category breakdown
  const catDivider  = document.getElementById('cat-divider');
  const catChartWrap = document.getElementById('cat-chart-wrap');
  const catBars     = document.getElementById('cat-bars');
  if (state.categories.length) {
    catDivider.style.display   = 'block';
    catChartWrap.style.display = 'block';
    const counts = {};
    state.categories.forEach(c => { counts[c] = (counts[c] || 0) + 1; });
    const maxCount = Math.max(...Object.values(counts));
    catBars.innerHTML = Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .map(([cat, cnt], i) => {
        const pct = Math.round(cnt / maxCount * 100);
        return `<div class="cat-row" style="animation-delay:${i * 0.05}s;">
          <div class="cat-name">${escHtml(cat)}</div>
          <div class="cat-bar-w"><div class="cat-bar-f" style="width:${pct}%;"></div></div>
          <div class="cat-count">${cnt}</div>
        </div>`;
      }).join('');
  } else {
    catDivider.style.display   = 'none';
    catChartWrap.style.display = 'none';
  }
}

// ─────────────────────────────────────────────
// SHARED: showAlert
// ─────────────────────────────────────────────
function showAlert(container, message, type = 'inf') {
  const cls  = { ok: 'alert-ok', err: 'alert-err', inf: 'alert-inf' }[type] || 'alert-inf';
  const icon = { ok: '✅', err: '❌', inf: 'ℹ️' }[type] || 'ℹ️';
  container.innerHTML = `<div class="alert ${cls}">${icon} &nbsp;${escHtml(message)}</div>`;
}

// ─────────────────────────────────────────────
// INIT
// ─────────────────────────────────────────────
renderPage(getPage());
