/**
 * api.js — FastAPI client for AI ATS
 * Uses relative paths so it works regardless of the port.
 */

const API_BASE = '';

/**
 * Check if the FastAPI backend is reachable.
 * @returns {Promise<boolean>}
 */
async function checkApiHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) });
    return res.ok;
  } catch {
    return false;
  }
}

/**
 * POST a single PDF to /predict
 * @param {File} file — PDF file object
 * @returns {Promise<{predicted_category: string, confidence: number}|{error: string}>}
 */
async function predictResume(file) {
  const form = new FormData();
  form.append('file', file, file.name);
  try {
    const res = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      body: form,
      signal: AbortSignal.timeout(30000),
    });
    const data = await res.json();
    if (!res.ok) return { error: data.error || `HTTP ${res.status}` };
    return data;
  } catch (err) {
    if (err.name === 'TimeoutError') return { error: 'Request timed out. Check the API server.' };
    return { error: 'Cannot reach API.' };
  }
}

/**
 * POST multiple PDFs + job description to /rank
 * @param {string} jobDescription
 * @param {FileList|File[]} files
 * @returns {Promise<{job_description: string, ranking: Array}|{error: string}>}
 */
async function rankResumes(jobDescription, files) {
  const form = new FormData();
  form.append('job_description', jobDescription);
  for (const file of files) {
    form.append('files', file, file.name);
  }
  try {
    const res = await fetch(`${API_BASE}/rank`, {
      method: 'POST',
      body: form,
      signal: AbortSignal.timeout(60000),
    });
    const data = await res.json();
    if (!res.ok) return { error: data.error || `HTTP ${res.status}` };
    return data;
  } catch (err) {
    if (err.name === 'TimeoutError') return { error: 'Request timed out. Check the API server.' };
    return { error: 'Cannot reach API.' };
  }
}
