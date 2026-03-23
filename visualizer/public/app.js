(() => {
  const scopeSelect = document.getElementById("scopeSelect");
  const topInput = document.getElementById("topInput");
  const connectionStatus = document.getElementById("connectionStatus");

  const metrics = {
    repos: document.getElementById("mRepos"),
    files: document.getElementById("mFiles"),
    functions: document.getElementById("mFunctions"),
    distinct: document.getElementById("mDistinct"),
    lastRepo: document.getElementById("mLastRepo"),
    lastUpdate: document.getElementById("mLastUpdate"),
  };

  const ctx = document.getElementById("rankingChart");
  const chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: [],
      datasets: [
        {
          label: "Conteo",
          data: [],
          borderWidth: 1,
          backgroundColor: "rgba(44, 123, 229, 0.7)",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
      },
      scales: {
        y: { beginAtZero: true },
      },
    },
  });

  let latestSnapshot = null;

  function topValue() {
    const n = Number(topInput.value);
    if (!Number.isFinite(n) || n <= 0) return 10;
    return Math.min(200, Math.floor(n));
  }

  function updateMetrics(stats) {
    if (!stats) return;
    metrics.repos.textContent = stats.totalReposProcessed ?? 0;
    metrics.files.textContent = stats.totalFilesProcessed ?? 0;
    metrics.functions.textContent = stats.totalFunctionsFound ?? 0;
    metrics.distinct.textContent = stats.totalDistinctWords ?? 0;
    metrics.lastRepo.textContent = stats.lastRepo || "-";
    metrics.lastUpdate.textContent = stats.lastUpdate || "-";
  }

  function renderRanking(items, scope) {
    chart.data.labels = items.map((i) => i.word);
    chart.data.datasets[0].data = items.map((i) => i.count);
    chart.data.datasets[0].label = `Conteo (${scope})`;
    chart.update();
  }

  async function fetchRankingAndStats() {
    const scope = scopeSelect.value;
    const top = topValue();

    const [rankingRes, statsRes] = await Promise.all([
      fetch(`/api/ranking?scope=${encodeURIComponent(scope)}&top=${encodeURIComponent(top)}`),
      fetch("/api/stats"),
    ]);

    if (!rankingRes.ok || !statsRes.ok) {
      return;
    }

    const ranking = await rankingRes.json();
    const stats = await statsRes.json();

    renderRanking(ranking.data || [], scope);
    updateMetrics(stats);
  }

  function renderFromSnapshot(snapshot) {
    if (!snapshot) return;
    const scope = scopeSelect.value;
    const top = topValue();

    const scopedData = snapshot.rankings?.[scope] || [];
    renderRanking(scopedData.slice(0, top), scope);
    updateMetrics(snapshot.stats);
  }

  function connectSse() {
    const source = new EventSource("/stream");

    source.addEventListener("connected", () => {
      connectionStatus.textContent = "Conectado";
      connectionStatus.className = "connected";
    });

    source.addEventListener("update", (event) => {
      try {
        const snapshot = JSON.parse(event.data);
        latestSnapshot = snapshot;
        renderFromSnapshot(snapshot);
      } catch (err) {
        console.error("Error parseando evento SSE", err);
      }
    });

    source.onerror = () => {
      connectionStatus.textContent = "Reconectando...";
      connectionStatus.className = "disconnected";
    };
  }

  scopeSelect.addEventListener("change", async () => {
    if (latestSnapshot) {
      renderFromSnapshot(latestSnapshot);
      return;
    }
    await fetchRankingAndStats();
  });

  topInput.addEventListener("change", async () => {
    topInput.value = String(topValue());
    if (latestSnapshot) {
      renderFromSnapshot(latestSnapshot);
      return;
    }
    await fetchRankingAndStats();
  });

  fetchRankingAndStats().catch((err) => console.error(err));
  connectSse();
})();
