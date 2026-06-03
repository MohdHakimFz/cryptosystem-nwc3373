(function initTheme() {
  const STORAGE_KEY = 'crypto-theme';
  const root = document.documentElement;

  function getSystemTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function getStoredTheme() {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === 'light' || stored === 'dark' ? stored : null;
  }

  function updateThemeSwitch(theme) {
    document.querySelectorAll('[data-set-theme]').forEach((btn) => {
      const isActive = btn.dataset.setTheme === theme;
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-pressed', String(isActive));
    });
  }

  function applyTheme(theme, animate) {
    if (animate) root.classList.add('theme-transition');
    root.setAttribute('data-theme', theme);
    root.style.colorScheme = theme;
    updateThemeSwitch(theme);
    window.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));

    if (animate) {
      window.setTimeout(() => root.classList.remove('theme-transition'), 350);
    }
  }

  function setTheme(theme, persist) {
    applyTheme(theme, true);
    if (persist) localStorage.setItem(STORAGE_KEY, theme);
  }

  const initial =
    root.getAttribute('data-theme') ||
    getStoredTheme() ||
    getSystemTheme();

  applyTheme(initial, false);

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (event) => {
    if (!getStoredTheme()) applyTheme(event.matches ? 'dark' : 'light', true);
  });

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-set-theme]').forEach((btn) => {
      btn.addEventListener('click', () => setTheme(btn.dataset.setTheme, true));
    });
    initKeyFieldButtons();
  });

  window.CryptoTheme = {
    get: () => root.getAttribute('data-theme'),
    set: (theme) => setTheme(theme, true),
    isDark: () => root.getAttribute('data-theme') === 'dark',
  };
})();

function showToast(message, type) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type || 'info'}`;
  toast.setAttribute('role', 'status');
  toast.textContent = message;
  container.appendChild(toast);

  requestAnimationFrame(() => toast.classList.add('toast-visible'));

  setTimeout(() => {
    toast.classList.remove('toast-visible');
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

async function copyKeyToClipboard(inputId) {
  const input = document.getElementById(inputId);
  if (!input?.value.trim()) {
    showToast('No key to copy. Generate or enter a key first.', 'error');
    return false;
  }

  try {
    await navigator.clipboard.writeText(input.value);
    showToast('Key copied to clipboard.', 'success');
    return true;
  } catch {
    input.type = 'text';
    input.focus();
    input.select();
    showToast('Select the key and copy manually (Ctrl+C).', 'info');
    return false;
  }
}

function toggleKeyVisibility(inputId) {
  const input = document.getElementById(inputId);
  const btn = document.querySelector(`.btn-toggle-key[data-target="${inputId}"]`);
  if (!input || !btn) return;

  const showing = input.type === 'text';
  input.type = showing ? 'password' : 'text';
  btn.setAttribute('aria-pressed', String(!showing));
  const label = btn.querySelector('.toggle-label');
  if (label) label.textContent = showing ? 'Show' : 'Hide';
}

async function generateSecureKey(inputId) {
  const input = document.getElementById(inputId);
  const btn = document.querySelector(`.btn-generate-key[data-target="${inputId}"]`);
  if (!input) return;

  const label = btn?.querySelector('.btn-generate-label');
  const originalLabel = label?.textContent;

  try {
    if (btn) {
      btn.disabled = true;
      if (label) label.textContent = '…';
    }

    const response = await fetch('/api/generate-key');
    const data = await response.json();

    if (!data.success) {
      showToast(data.error || 'Could not generate key.', 'error');
      return;
    }

    input.value = data.key;
    input.type = 'text';
    const toggleBtn = document.querySelector(`.btn-toggle-key[data-target="${inputId}"]`);
    if (toggleBtn) {
      toggleBtn.setAttribute('aria-pressed', 'true');
      const toggleLabel = toggleBtn.querySelector('.toggle-label');
      if (toggleLabel) toggleLabel.textContent = 'Hide';
    }

    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.focus();
    input.select();

    const copied = await copyKeyToClipboard(inputId);
    if (!copied) {
      showToast('Key generated — use Copy Key or select text to copy.', 'success');
    }
  } catch {
    showToast('Network error. Please try again.', 'error');
  } finally {
    if (btn) {
      btn.disabled = false;
      if (label && originalLabel) label.textContent = originalLabel;
    }
  }
}

function initKeyFieldButtons() {
  document.querySelectorAll('.btn-generate-key').forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetId = btn.dataset.target;
      if (targetId) generateSecureKey(targetId);
    });
  });

  document.querySelectorAll('.btn-copy-key').forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetId = btn.dataset.target;
      if (targetId) copyKeyToClipboard(targetId);
    });
  });

  document.querySelectorAll('.btn-toggle-key').forEach((btn) => {
    btn.addEventListener('click', () => {
      const targetId = btn.dataset.target;
      if (targetId) toggleKeyVisibility(targetId);
    });
  });
}

function setupAlgoToggle(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return () => 'lfsr';

  container.querySelectorAll('.algo-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      container.querySelectorAll('.algo-btn').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });

  return () => container.querySelector('.algo-btn.active').dataset.algo;
}

function setupFileDrop(zoneId, inputId, nameId) {
  const zone = document.getElementById(zoneId);
  const input = document.getElementById(inputId);
  const nameEl = document.getElementById(nameId);
  if (!zone || !input) return;

  function updateName() {
    if (!nameEl) return;
    if (input.files.length) {
      nameEl.textContent = input.files[0].name;
      nameEl.classList.remove('hidden');
    } else {
      nameEl.textContent = '';
      nameEl.classList.add('hidden');
    }
  }

  // Label[for] opens the picker once — do not call input.click() again (double-dialog bug).
  zone.addEventListener('dragover', (e) => {
    e.preventDefault();
    zone.classList.add('dragover');
  });

  zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));

  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
      input.files = e.dataTransfer.files;
      updateName();
    }
  });

  input.addEventListener('change', updateName);
}

async function parseJsonError(response, fallback) {
  try {
    const data = await response.json();
    return data.error || fallback;
  } catch {
    return fallback;
  }
}

async function handleEncryptedFileDownload(response, defaultName, onSuccess, onError) {
  const contentType = response.headers.get('content-type') || '';

  if (!response.ok || contentType.includes('application/json')) {
    const message = await parseJsonError(
      response,
      'Incorrect decryption key. Please try again.',
    );
    onError(message);
    return;
  }

  const blob = await response.blob();
  const disposition = response.headers.get('Content-Disposition') || '';
  const match = disposition.match(/filename="?([^";]+)"?/);
  const filename = match ? match[1] : defaultName;
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
  onSuccess(filename);
}
