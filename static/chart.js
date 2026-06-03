let perfChart = null;

function getChartColors() {
  const isDark = window.CryptoTheme?.isDark?.() ?? false;
  return {
    lfsr: isDark ? '#2ee4b0' : '#1d9e75',
    feistel: isDark ? '#9d94f0' : '#534ab7',
    grid: getComputedStyle(document.documentElement).getPropertyValue('--chart-grid').trim(),
    text: getComputedStyle(document.documentElement).getPropertyValue('--chart-text').trim(),
    surface: getComputedStyle(document.documentElement).getPropertyValue('--surface').trim(),
  };
}

function buildChartOptions(colors) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: { color: colors.text, font: { family: 'Fira Sans', size: 12 } },
      },
      title: {
        display: true,
        text: 'Encryption Time Comparison (ms)',
        color: colors.text,
        font: { family: 'Fira Sans', size: 14, weight: '600' },
      },
    },
    scales: {
      x: {
        ticks: { color: colors.text },
        grid: { color: colors.grid },
      },
      y: {
        beginAtZero: true,
        ticks: { color: colors.text },
        grid: { color: colors.grid },
        title: {
          display: true,
          text: 'Milliseconds',
          color: colors.text,
        },
      },
    },
  };
}

function renderChart(results) {
  const sizes = ['1kb', '100kb', '1mb'];
  const labels = ['1 KB', '100 KB', '1 MB'];
  const colors = getChartColors();

  const lfsrData = sizes.map((size) => results.lfsr[size].encrypt_ms);
  const feistelData = sizes.map((size) => results.feistel[size].encrypt_ms);

  const ctx = document.getElementById('perf-chart').getContext('2d');
  if (perfChart) perfChart.destroy();

  perfChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Galois LFSR',
          backgroundColor: colors.lfsr,
          borderColor: colors.lfsr,
          borderRadius: 6,
          data: lfsrData,
        },
        {
          label: 'Feistel Cipher',
          backgroundColor: colors.feistel,
          borderRadius: 6,
          data: feistelData,
        },
      ],
    },
    options: buildChartOptions(colors),
  });
}

function renderResults(results) {
  const sizes = ['1kb', '100kb', '1mb'];
  const labels = ['1 KB', '100 KB', '1 MB'];
  const tbody = document.getElementById('results-body');

  tbody.innerHTML = '';
  sizes.forEach((size, index) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${labels[index]}</td>
      <td>${results.lfsr[size].encrypt_ms}</td>
      <td>${results.lfsr[size].decrypt_ms}</td>
      <td>${results.feistel[size].encrypt_ms}</td>
      <td>${results.feistel[size].decrypt_ms}</td>
    `;
    tbody.appendChild(row);
  });

  const allEncryptTimes = sizes.flatMap((size) => [
    results.lfsr[size].encrypt_ms,
    results.feistel[size].encrypt_ms,
  ]);
  const fastest = Math.min(...allEncryptTimes);
  const slowest = Math.max(...allEncryptTimes);

  document.getElementById('stats-row').innerHTML = `
    <div class="stat-card">
      <div class="stat-value">${fastest}</div>
      <div class="stat-label">Fastest Encrypt (ms)</div>
    </div>
    <div class="stat-card secondary">
      <div class="stat-value">${slowest}</div>
      <div class="stat-label">Slowest Encrypt (ms)</div>
    </div>
  `;

  renderChart(results);
}

document.getElementById('run-benchmark-btn').addEventListener('click', async () => {
  const btn = document.getElementById('run-benchmark-btn');
  const loading = document.getElementById('loading');
  const resultsSection = document.getElementById('results-section');
  const errorBox = document.getElementById('benchmark-error');

  btn.disabled = true;
  loading.classList.remove('hidden');
  resultsSection.classList.add('hidden');
  errorBox.classList.add('hidden');

  try {
    const response = await fetch('/api/benchmark', { method: 'POST' });
    const data = await response.json();

    if (!data.success) {
      errorBox.textContent = data.error || 'Benchmark failed.';
      errorBox.classList.remove('hidden');
      return;
    }

    renderResults(data.results);
    resultsSection.classList.remove('hidden');
    showToast('Benchmark completed', 'success');
  } catch {
    errorBox.textContent = 'Network error. Please try again.';
    errorBox.classList.remove('hidden');
  } finally {
    btn.disabled = false;
    loading.classList.add('hidden');
  }
});

window.addEventListener('themechange', () => {
  if (perfChart && perfChart.data.datasets.length) {
    const colors = getChartColors();
    perfChart.data.datasets[0].backgroundColor = colors.lfsr;
    perfChart.data.datasets[1].backgroundColor = colors.feistel;
    perfChart.options = buildChartOptions(colors);
    perfChart.update();
  }
});
