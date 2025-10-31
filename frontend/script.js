const $ = (sel) => document.querySelector(sel);

const fileInput = $('#fileInput');
const okBtn = $('#okBtn');
const cancelBtn = $('#cancelBtn');
const bar = $('#bar');
const progress = $('#progress');
const statusEl = $('#status');
const preview = $('#preview');
const downloadLink = $('#downloadLink');

let currentJobId = null;
let pollTimer = null;

const BACKEND = window.BACKEND_BASE || 'http://localhost:8000';

function resetUI() {
  currentJobId = null;
  if (pollTimer) clearInterval(pollTimer);
  okBtn.disabled = !fileInput.files.length;
  cancelBtn.disabled = true;
  bar.style.width = '0%';
  progress.classList.add('hidden');
  statusEl.textContent = '';
  preview.classList.add('hidden');
  preview.src = '';
  downloadLink.classList.add('hidden');
  downloadLink.href = '#';
}

fileInput.addEventListener('change', () => {
  resetUI();
  okBtn.disabled = !fileInput.files.length;
});

okBtn.addEventListener('click', async () => {
  if (!fileInput.files.length) return;
  progress.classList.remove('hidden');
  bar.style.width = '5%';
  statusEl.textContent = 'Uploading...';
  okBtn.disabled = true;
  cancelBtn.disabled = false;

  const form = new FormData();
  form.append('file', fileInput.files[0]);

  try {
    const res = await fetch(`${BACKEND}/api/jobs`, {
      method: 'POST',
      body: form
    });
    if (!res.ok) throw new Error('Failed to create job');
    const data = await res.json();
    currentJobId = data.job_id;
    startPolling();
  } catch (e) {
    statusEl.textContent = 'Error: ' + e.message;
    cancelBtn.disabled = true;
    okBtn.disabled = false;
  }
});

cancelBtn.addEventListener('click', async () => {
  if (!currentJobId) return;
  cancelBtn.disabled = true;
  statusEl.textContent = 'Cancelling...';
  try {
    await fetch(`${BACKEND}/api/jobs/${currentJobId}`, { method: 'DELETE' });
  } catch (e) {
    // ignore
  }
});

function startPolling() {
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(async () => {
    if (!currentJobId) return;
    try {
      const res = await fetch(`${BACKEND}/api/jobs/${currentJobId}`);
      if (!res.ok) throw new Error('Status check failed');
      const job = await res.json();
      const pct = Math.max(0, Math.min(100, job.progress || 0));
      bar.style.width = pct + '%';
      statusEl.textContent = `${job.status} - ${job.message || ''}`;

      if (job.status === 'completed') {
        clearInterval(pollTimer);
        cancelBtn.disabled = true;
        const resultUrl = `${BACKEND}/api/jobs/${currentJobId}/result`;
        preview.src = resultUrl;
        preview.classList.remove('hidden');
        downloadLink.href = resultUrl;
        downloadLink.download = `${currentJobId}.png`;
        downloadLink.classList.remove('hidden');
      } else if (job.status === 'failed' || job.status === 'cancelled') {
        clearInterval(pollTimer);
        cancelBtn.disabled = true;
      }
    } catch (e) {
      // show but keep trying briefly
      statusEl.textContent = 'Polling error: ' + e.message;
    }
  }, 800);
}

// Init
resetUI();

