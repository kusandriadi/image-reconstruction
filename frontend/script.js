const $ = (sel) => document.querySelector(sel);

const fileInput = $('#fileInput');
const okBtn = $('#okBtn');
const cancelBtn = $('#cancelBtn');
const bar = $('#bar');
const progress = $('#progress');
const statusEl = $('#status');
const preview = $('#preview');
const downloadLink = $('#downloadLink');
const dropZone = $('#dropZone');
const filePreview = $('#filePreview');
const progressPercent = $('#progressPercent');
const progressText = $('#progressText');
const outputPlaceholder = $('#outputPlaceholder');

let currentJobId = null;
let pollTimer = null;

// Configuration from centralized config via backend API
// No hardcoded defaults - will be loaded from backend
let appConfig = null;

// Get BACKEND URL from localStorage or fetch from config
let BACKEND = window.BACKEND_BASE;

// Load configuration from backend on startup
async function loadConfig() {
  try {
    // If no BACKEND set, try to get from config
    if (!BACKEND) {
      BACKEND = 'http://localhost:8000'; // Temporary default just for initial config fetch
    }

    const res = await fetch(`${BACKEND}/api/config`);
    if (res.ok) {
      appConfig = await res.json();

      // Update BACKEND URL from config if not set by localStorage
      if (!window.BACKEND_BASE) {
        BACKEND = appConfig.backend_url;
      }

      console.log('Configuration loaded from backend:', appConfig);

      // Apply UI configuration
      applyUIConfig();
    } else {
      console.error('Failed to load config from backend');
      throw new Error('Config load failed');
    }
  } catch (e) {
    console.error('Could not fetch config from backend:', e.message);
    alert('Failed to load application configuration. Please ensure the backend is running.');
    throw e;
  }
}

// Apply UI configuration from loaded config
function applyUIConfig() {
  if (!appConfig) return;

  // Update page title
  if (appConfig.ui?.title) {
    document.title = appConfig.ui.title;
    const h1 = document.querySelector('h1');
    if (h1) h1.textContent = appConfig.ui.title;
  }

  // Update labels
  if (appConfig.ui?.labels) {
    const inputLabel = document.querySelector('label[class="label"]:first-of-type');
    if (inputLabel) inputLabel.textContent = appConfig.ui.labels.input;

    const outputLabel = document.querySelector('label[class="label"]:last-of-type');
    if (outputLabel) outputLabel.textContent = appConfig.ui.labels.output;

    if (okBtn) okBtn.textContent = appConfig.ui.labels.ok_button;
    if (cancelBtn) cancelBtn.textContent = appConfig.ui.labels.cancel_button;
    if (downloadLink) downloadLink.textContent = appConfig.ui.labels.download_button;
  }

  // Update file input accept attribute
  if (appConfig.file_input?.accept && fileInput) {
    fileInput.setAttribute('accept', appConfig.file_input.accept);
  }

  // Update preview alt text
  if (appConfig.ui?.preview_alt_text && preview) {
    preview.alt = appConfig.ui.preview_alt_text;
  }
}

// Helper function to format message templates
function formatMessage(template, params) {
  if (!template) return '';
  let message = template;
  for (const [key, value] of Object.entries(params)) {
    message = message.replace(`{${key}}`, value);
  }
  return message;
}

function resetUI() {
  currentJobId = null;
  if (pollTimer) clearInterval(pollTimer);
  okBtn.disabled = !fileInput.files.length;
  cancelBtn.disabled = true;
  bar.style.width = '0%';
  if (progressPercent) progressPercent.textContent = '0%';
  progress.classList.add('hidden');
  statusEl.textContent = '';
  preview.classList.add('hidden');
  preview.src = '';
  downloadLink.classList.add('hidden');
  downloadLink.href = '#';
  if (outputPlaceholder) outputPlaceholder.classList.remove('hidden');
}

function showFilePreview(file) {
  if (filePreview) {
    filePreview.textContent = `📄 ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
    filePreview.classList.remove('hidden');
  }
}

function updateProgress(percent) {
  bar.style.width = percent + '%';
  if (progressPercent) {
    progressPercent.textContent = Math.round(percent) + '%';
  }
}

function handleFileSelect(file) {
  // Validate file on selection
  if (file && appConfig) {
    const fileSizeMB = file.size / (1024 * 1024);

    if (fileSizeMB > appConfig.upload.max_size_mb) {
      const msg = formatMessage(appConfig.ui.messages.file_too_large, {
        max_size: appConfig.upload.max_size_mb
      });
      statusEl.textContent = `Error: ${msg}`;
      okBtn.disabled = true;
      return;
    }

    const fileExt = '.' + file.name.split('.').pop().toLowerCase();
    if (!appConfig.upload.allowed_extensions.includes(fileExt)) {
      const msg = formatMessage(appConfig.ui.messages.file_type_not_allowed, {
        allowed_types: appConfig.upload.allowed_extensions.join(', ')
      });
      statusEl.textContent = `Error: ${msg}`;
      okBtn.disabled = true;
      return;
    }

    showFilePreview(file);
    okBtn.disabled = false;
  }
}

fileInput.addEventListener('change', () => {
  resetUI();
  okBtn.disabled = !fileInput.files.length;

  if (fileInput.files.length > 0) {
    handleFileSelect(fileInput.files[0]);
  }
});

// Drag and drop functionality
if (dropZone) {
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  ['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => {
      dropZone.classList.add('drag-over');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => {
      dropZone.classList.remove('drag-over');
    }, false);
  });

  dropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;

    if (files.length > 0) {
      fileInput.files = files;
      resetUI();
      handleFileSelect(files[0]);
    }
  }, false);
}

okBtn.addEventListener('click', async () => {
  if (!fileInput.files.length || !appConfig) return;

  // Show progress bar only if enabled in config
  if (appConfig.ui.show_progress_bar) {
    progress.classList.remove('hidden');
  }
  updateProgress(5);
  if (progressText) progressText.textContent = 'Uploading...';
  statusEl.textContent = appConfig.ui.messages.uploading;
  okBtn.disabled = true;
  cancelBtn.disabled = false;

  const form = new FormData();
  form.append('file', fileInput.files[0]);

  try {
    const res = await fetch(`${BACKEND}/api/jobs`, {
      method: 'POST',
      body: form
    });
    if (!res.ok) throw new Error(appConfig.ui.messages.create_job_failed);
    const data = await res.json();
    currentJobId = data.job_id;
    if (progressText) progressText.textContent = 'Processing...';
    startPolling();
  } catch (e) {
    statusEl.textContent = 'Error: ' + e.message;
    cancelBtn.disabled = true;
    okBtn.disabled = false;
  }
});

cancelBtn.addEventListener('click', async () => {
  if (!currentJobId || !appConfig) return;
  cancelBtn.disabled = true;
  statusEl.textContent = appConfig.ui.messages.cancelling;
  try {
    await fetch(`${BACKEND}/api/jobs/${currentJobId}`, { method: 'DELETE' });
  } catch (e) {
    // ignore
  }
});

function startPolling() {
  if (pollTimer) clearInterval(pollTimer);
  if (!appConfig) return;

  // Use polling interval from config
  const pollingInterval = appConfig.polling.interval_ms;

  pollTimer = setInterval(async () => {
    if (!currentJobId) return;
    try {
      const res = await fetch(`${BACKEND}/api/jobs/${currentJobId}`);
      if (!res.ok) throw new Error('Status check failed');
      const job = await res.json();
      const pct = Math.max(0, Math.min(100, job.progress || 0));
      updateProgress(pct);
      statusEl.textContent = `${job.status} - ${job.message || ''}`;

      if (job.status === 'completed') {
        clearInterval(pollTimer);
        cancelBtn.disabled = true;
        if (progressText) progressText.textContent = 'Completed!';
        const resultUrl = `${BACKEND}/api/jobs/${currentJobId}/result`;

        // Hide output placeholder
        if (outputPlaceholder) outputPlaceholder.classList.add('hidden');

        // Show preview only if enabled in config
        if (appConfig.ui.preview_enabled) {
          preview.src = resultUrl;
          preview.classList.remove('hidden');
        }

        // Show download link only if enabled in config
        if (appConfig.ui.download_enabled) {
          downloadLink.href = resultUrl;
          downloadLink.download = `${currentJobId}.png`;
          downloadLink.classList.remove('hidden');
        }
      } else if (job.status === 'failed' || job.status === 'cancelled') {
        clearInterval(pollTimer);
        cancelBtn.disabled = true;
        if (progressText) progressText.textContent = job.status === 'failed' ? 'Failed' : 'Cancelled';
      }
    } catch (e) {
      // show but keep trying briefly
      const msg = formatMessage(appConfig.ui.messages.polling_error, { error: e.message });
      statusEl.textContent = msg;
    }
  }, pollingInterval);
}

// Initialize app
async function init() {
  await loadConfig();
  resetUI();
  console.log('Image Reconstruction UI initialized with config:', appConfig);
}

// Run initialization
init();

