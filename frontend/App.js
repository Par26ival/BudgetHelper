const API_URL = "http://localhost:5000/transactions";

const form = document.getElementById("transactionForm");
const list = document.getElementById("transactionList");
const predictionText = document.getElementById("prediction");
const predictBtn = document.getElementById("predictButton");
const forecastList = document.getElementById("forecastList");

let dailyChartInstance = null;
let monthlyChartInstance = null;

// Load and display transaction history
async function loadTransactions() {
  try {
    const res = await fetch(API_URL);
    const data = await res.json();

    list.innerHTML = "";

    data.reverse().forEach((t) => {
      const item = document.createElement("li");
      item.className = t.type === "income" ? "income" : "";
      item.innerText = `${t.date} — ${t.description} — ${t.amount.toFixed(2)} BGN [${t.category}] (${t.type})`;
      list.appendChild(item);
    });
  } catch (err) {
    console.error("Error loading transactions:", err);
  }
}

// Handle transaction form submit
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const amount = parseFloat(document.getElementById("amount").value);
  const description = document.getElementById("description").value.trim();
  const date = document.getElementById("date").value;
  const type = document.querySelector('input[name="type"]:checked').value;

  if (!description || isNaN(amount) || !date) return;

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount, description, date, type }),
    });

    if (!res.ok) throw new Error("Failed to add transaction");

    const data = await res.json();
    predictionText.innerText = `Predicted category: ${data.category}`;
    form.reset();
    loadTransactions();
    loadDailyChart(); // refresh daily chart
    loadMonthlyChart(); // refresh monthly chart
  } catch (error) {
    console.error("Error submitting transaction:", error);
  }
});

// Handle prediction button click
predictBtn.addEventListener("click", async () => {
  try {
    const res = await fetch("http://localhost:5000/predict");
    if (!res.ok) throw new Error("Prediction API failed");
    const data = await res.json();

    forecastList.innerHTML = "";

    const { forecast, total_income, total_spending, net_savings } = data;

    const summary = document.createElement("li");
    summary.innerHTML = `
      <strong>💰 Forecast Summary:</strong><br>
      Expected Income: <b>${total_income.toFixed(2)} BGN</b><br>
      Expected Spending: <b>${total_spending.toFixed(2)} BGN</b><br>
      Estimated Savings: <b>${net_savings.toFixed(2)} BGN</b>
    `;
    forecastList.appendChild(summary);

    if (forecast && forecast.length > 0) {
      const grouped = forecast.reduce((acc, item) => {
        if (!acc[item.type]) acc[item.type] = [];
        acc[item.type].push(item);
        return acc;
      }, {});

      for (const [type, items] of Object.entries(grouped)) {
        const groupHeader = document.createElement("li");
        groupHeader.innerHTML = `<strong>${type.toUpperCase()}:</strong>`;
        forecastList.appendChild(groupHeader);

        items.forEach(item => {
          const li = document.createElement("li");
          li.innerText = `${item.date} — ${item.description}: ${item.amount.toFixed(2)} BGN (${item.type}) × ${item.expected_occurrences} = ${item.total_estimate.toFixed(2)} BGN`;
          forecastList.appendChild(li);
        });
      }
    } else {
      forecastList.innerHTML += `<li>No predictable transactions for next month yet.</li>`;
    }
  } catch (error) {
    console.error("Error fetching prediction:", error);
  }
});

// Load monthly spending chart
async function loadMonthlyChart() {
  try {
    const res = await fetch("http://localhost:5000/api/stats/monthly");
    if (!res.ok) throw new Error("Failed to fetch monthly stats");
    const data = await res.json();

    const labels = data.map(item => item.month);
    const values = data.map(item => item.total_spent);

    const ctx = document.getElementById("monthlyChart").getContext("2d");

    if (monthlyChartInstance) monthlyChartInstance.destroy();

    monthlyChartInstance = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [{
          label: "Total Monthly Spending (BGN)",
          data: values,
          fill: true,
          borderColor: "#e26a00",
          backgroundColor: "rgba(226, 106, 0, 0.3)",
          tension: 0.4,
          pointRadius: 4,
          borderWidth: 2,
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: "BGN" }
          }
        },
        plugins: {
          legend: { display: true },
          tooltip: {
            callbacks: {
              label: ctx => `Spending: ${ctx.parsed.y.toFixed(2)} BGN`
            }
          }
        }
      }
    });
  } catch (error) {
    console.error("Error loading monthly chart:", error);
  }
}

// Initial page load
window.addEventListener("DOMContentLoaded", () => {
  loadTransactions();
  loadDailyChart();
  loadMonthlyChart();
});
