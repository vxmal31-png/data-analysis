(function () {
  const html = document.documentElement;
  const savedTheme = localStorage.getItem("visitor-theme") || "dark";
  html.dataset.theme = savedTheme;

  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebarOverlay");
  document.getElementById("themeToggle").addEventListener("click", () => {
    html.dataset.theme = html.dataset.theme === "dark" ? "light" : "dark";
    localStorage.setItem("visitor-theme", html.dataset.theme);
  });
  document.getElementById("collapseSidebar").addEventListener("click", () => sidebar.classList.toggle("collapsed"));
  document.getElementById("menuButton").addEventListener("click", () => {
    sidebar.classList.add("mobile-open");
    overlay.classList.add("show");
  });
  overlay.addEventListener("click", () => {
    sidebar.classList.remove("mobile-open");
    overlay.classList.remove("show");
  });

  function showToast(message) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.classList.add("show");
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(() => toast.classList.remove("show"), 2600);
  }

  const chartTheme = () => ({
    grid: html.dataset.theme === "dark" ? "rgba(148,163,184,.10)" : "rgba(100,116,139,.12)",
    text: html.dataset.theme === "dark" ? "#98a4b8" : "#718096"
  });

  async function getChartData() {
    const response = await fetch("/api/chart-data");
    if (!response.ok) throw new Error("Could not load chart data");
    return response.json();
  }

  function baseChartOptions() {
    const theme = chartTheme();
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { backgroundColor: "#172033", padding: 10 } },
      scales: {
        x: { ticks: { color: theme.text, maxTicksLimit: 8 }, grid: { display: false } },
        y: { ticks: { color: theme.text }, grid: { color: theme.grid } }
      }
    };
  }

  if (window.pageChart === "overview") {
    getChartData().then(data => {
      new Chart(document.getElementById("overviewChart"), {
        type: "line",
        data: { labels: data.dates, datasets: [{ data: data.visitors, borderColor: "#6366f1", backgroundColor: "rgba(99,102,241,.12)", fill: true, tension: .35, pointRadius: 0 }] },
        options: baseChartOptions()
      });
    }).catch(error => showToast(error.message));
  }

  if (window.pageChart === "analytics") {
    getChartData().then(data => {
      const target = data.target.filter((value) => value !== null);
      const metricRoot = document.getElementById("analyticsMetrics");
      metricRoot.innerHTML =
        `<article class="metric-card"><div class="metric-icon cyan">↗</div><div><p>Total visitors</p><h2>${target.reduce((a,b)=>a+b,0).toLocaleString()}</h2><small>Historical total</small></div></article>` +
        `<article class="metric-card"><div class="metric-icon violet">∿</div><div><p>Average visitors</p><h2>${(target.reduce((a,b)=>a+b,0)/Math.max(target.length,1)).toLocaleString(undefined,{maximumFractionDigits:1})}</h2><small>Dataset average</small></div></article>` +
        `<article class="metric-card"><div class="metric-icon blue">↓</div><div><p>Minimum</p><h2>${Math.min(...target).toLocaleString()}</h2><small>Lowest record</small></div></article>` +
        `<article class="metric-card"><div class="metric-icon green">↑</div><div><p>Maximum</p><h2>${Math.max(...target).toLocaleString()}</h2><small>Highest record</small></div></article>`;

      new Chart(document.getElementById("trendChart"), {
        type: "line",
        data: { labels: data.dates, datasets: [{ data: data.visitors, borderColor: "#06b6d4", backgroundColor: "rgba(6,182,212,.10)", fill: true, tension: .35, pointRadius: 0 }] },
        options: baseChartOptions()
      });

      const bins = 12;
      const min = Math.min(...target), max = Math.max(...target);
      const width = (max - min) / bins || 1;
      const counts = Array(bins).fill(0);
      target.forEach(value => counts[Math.min(bins - 1, Math.floor((value - min) / width))]++);
      new Chart(document.getElementById("distributionChart"), {
        type: "bar",
        data: { labels: counts.map((_, i) => `${Math.round(min + i * width)}`), datasets: [{ data: counts, backgroundColor: "rgba(124,58,237,.72)", borderRadius: 5 }] },
        options: baseChartOptions()
      });

      const correlation = data.correlation;
      if (Object.keys(correlation).length) {
        const labels = Object.keys(correlation);
        const values = labels.map(label => correlation[label][labels[1]] ?? 0);
        new Chart(document.getElementById("correlationChart"), {
          type: "bar",
          data: { labels, datasets: [{ data: values, backgroundColor: labels.map((_, i) => i % 2 ? "rgba(6,182,212,.72)" : "rgba(99,102,241,.72)"), borderRadius: 5 }] },
          options: baseChartOptions()
        });
      } else {
        document.getElementById("correlationChart").closest(".panel").style.display = "none";
      }
    }).catch(error => showToast(error.message));
  }

  if (window.pageChart === "dataset") {
    let page = 1, search = "";
    async function loadDataset() {
      const response = await fetch(`/api/dataset?page=${page}&per_page=25&search=${encodeURIComponent(search)}`);
      const data = await response.json();
      const table = document.getElementById("datasetTable");
      table.querySelector("thead").innerHTML = `<tr>${data.columns.map(column => `<th>${column}</th>`).join("")}</tr>`;
      table.querySelector("tbody").innerHTML = data.records.length
        ? data.records.map(record => `<tr>${data.columns.map(column => `<td>${record[column] ?? ""}</td>`).join("")}</tr>`).join("")
        : `<tr><td colspan="${data.columns.length}">No matching records found.</td></tr>`;
      document.getElementById("tableCount").textContent = `${data.total} records`;
      document.getElementById("pageInfo").textContent = `Page ${data.page} of ${data.pages}`;
      document.getElementById("prevPage").disabled = page <= 1;
      document.getElementById("nextPage").disabled = page >= data.pages;
    }
    document.getElementById("datasetSearch").addEventListener("input", (event) => { search = event.target.value; page = 1; loadDataset(); });
    document.getElementById("prevPage").addEventListener("click", () => { if (page > 1) { page--; loadDataset(); } });
    document.getElementById("nextPage").addEventListener("click", () => { page++; loadDataset(); });
    loadDataset();
  }

  if (window.pageChart === "performance") {
    const metrics = window.modelMetrics || {};
    const labels = ["MAE", "RMSE", "Baseline_MAE"].filter(key => typeof metrics[key] === "number");
    const values = labels.map(key => metrics[key]);
    new Chart(document.getElementById("metricChart"), {
      type: "bar",
      data: { labels: labels.map(label => label.replace("_", " ")), datasets: [{ data: values, backgroundColor: ["rgba(6,182,212,.72)","rgba(124,58,237,.72)","rgba(59,130,246,.72)"], borderRadius: 6 }] },
      options: baseChartOptions()
    });
  }

  const predictionForm = document.getElementById("predictionForm");
  if (predictionForm) {
    document.getElementById("clearPrediction").addEventListener("click", () => {
      predictionForm.reset();
      (window.modelFeatures || []).forEach(feature => {
        const input = predictionForm.elements[feature];
        if (input) input.value = window.modelDefaults[feature] ?? 0;
      });
      document.getElementById("predictionResult").hidden = true;
      document.getElementById("resultEmpty").hidden = false;
    });
    predictionForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (!predictionForm.reportValidity()) return;
      const button = document.getElementById("predictButton");
      button.disabled = true;
      button.textContent = "Predicting...";
      const payload = {};
      new FormData(predictionForm).forEach((value, key) => payload[key] = value);
      try {
        const response = await fetch("/api/predict", { method:"POST", headers:{ "Content-Type":"application/json" }, body:JSON.stringify(payload) });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Prediction failed");
        document.getElementById("resultEmpty").hidden = true;
        const result = document.getElementById("predictionResult");
        result.hidden = false;
        document.getElementById("predictionValue").textContent = data.prediction_display;
        showToast("Prediction completed");
      } catch (error) {
        showToast(error.message);
      } finally {
        button.disabled = false;
        button.innerHTML = "Predict visitors <span>→</span>";
      }
    });
  }

  const globalSearch = document.getElementById("globalSearch");
  if (globalSearch) globalSearch.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      window.location.href = "/dataset";
    }
  });
})();
