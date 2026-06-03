// ====================
// Get Data
// ====================

const pieLabels = window.chartData.pieLabels;
const pieValues = window.chartData.pieValues;

const barLabels = window.chartData.barLabels;
const barValues = window.chartData.barValues;

const lineLabels = window.chartData.lineLabels;
const lineValues = window.chartData.lineValues;

// ====================
// Pie Chart
// ====================

new Chart(document.getElementById("pieChart"), {
  type: "pie",

  data: {
    labels: pieLabels,

    datasets: [
      {
        data: pieValues,
      },
    ],
  },

  options: {
    responsive: true,
    maintainAspectRatio: false,

    plugins: {
      legend: {
        position: "bottom",
      },
    },
  },
});

// ====================
// Bar Chart
// ====================

new Chart(document.getElementById("barChart"), {
  type: "bar",

  data: {
    labels: barLabels,

    datasets: [
      {
        label: "Total Spending (NT$)",
        data: barValues,
      },
    ],
  },

  options: {
    responsive: true,
    maintainAspectRatio: false,

    plugins: {
      legend: {
        display: false,
      },
    },

    scales: {
      y: {
        beginAtZero: true,
      },
    },
  },
});

// ====================
// Line Chart
// ====================

new Chart(document.getElementById("lineChart"), {
  type: "line",

  data: {
    labels: lineLabels,

    datasets: [
      {
        label: "Daily Spending (NT$)",
        data: lineValues,
        fill: false,
        tension: 0.4,
        borderWidth: 3,
        pointRadius: 5,
      },
    ],
  },

  options: {
    responsive: true,
    maintainAspectRatio: false,

    plugins: {
      legend: {
        position: "bottom",
      },
    },

    animation: {
      duration: 1200,
    },

    scales: {
      y: {
        beginAtZero: true,
      },
    },
  },
});
