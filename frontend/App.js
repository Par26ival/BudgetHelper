const API_BASE_URL = "http://localhost:5000"; // Adjust if needed

const form = document.getElementById("transactionForm");
const list = document.getElementById("transactionList");
const predictionText = document.getElementById("prediction");
const predictBtn = document.getElementById("predictButton");
const forecastList = document.getElementById("forecastList");
const logoutButton = document.getElementById("logoutButton");
const spendingChartCtx = document.getElementById("spendingChart").getContext("2d");

let spendingChartInstance = null;

// Utility to check fetch response and redirect if unauthorized
async function checkResponse(response) {
  if (response.status === 401) {
    window.location.href = `${API_BASE_URL}/login`;
    throw new Error("Unauthorized, redirecting to login...");
  }
  if (!response.ok) {
    const errData = await response.json();
    throw new Error(errData.message || "API error");
  }
  return response.json();
}

// Load and display transactions
async function loadTransactions() {
  try {
    const res = await fetch(`${API_BASE_URL}/transactions`);
    const data = await checkResponse(res);

    list.innerHTML = "";
    data.reverse().forEach(t => {
      const li = document.createElement("li");
      li.className = t.type === "income" ? "income" : "";
      li.textContent = `${t.date} — ${t.description} — ${t.amount.toFixed(2)} BGN [${t.category}] (${t.type})`;
      list.appendChild(li);
    });
  } catch (error) {
    console.error("Error loading transactions:", error);
  }
}

// Handle new transaction submission
form.addEventListener("submit", async e => {
  e.preventDefault();

  const amount = parseFloat(document.getElementById("amount").value);
  const description = document.getElementById("description").value.trim();
  const date = document.getElementById("date").value;
  const type = document.querySelector('input[name="type"]:checked').value; // "spending" or "income"

  if (!description || isNaN(amount) || !date) return;

  // Convert "spending" to "expense" for backend if needed, or keep as is
  // Adjust depending on your backend expectations
  const normalizedType = (type === "spending") ? "expense" : "income";

  try {
    const res = await fetch(`${API_BASE_URL}/transactions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount, description, date, type: normalizedType }),
    });
    const data = await checkResponse(res);

    predictionText.textContent = `Predicted category: ${data.category}`;
    form.reset();
    loadTransactions();
    loadSpendingChart();
  } catch (error) {
    console.error("Error submitting transaction:", error);
  }
});

predictBtn.addEventListener("click", async () => {
  try {
    const res = await fetch("http://localhost:5000/predict");
    if (!res.ok) throw new Error("Prediction API failed");
    const data = await res.json();

    forecastList.innerHTML = "";  // clear old forecast

    // Display summary
    const summary = document.createElement("li");
    summary.innerHTML = `
      <strong>💰 Forecast Summary:</strong><br>
      Expected Income: <b>${data.total_income.toFixed(2)} BGN</b><br>
      Expected Spending: <b>${data.total_spending.toFixed(2)} BGN</b><br>
      Estimated Savings: <b>${data.net_savings.toFixed(2)} BGN</b>
    `;
    forecastList.appendChild(summary);

    if (data.forecast && data.forecast.length > 0) {
      // Group forecast by type (income/spending)
      const grouped = data.forecast.reduce((acc, item) => {
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
    forecastList.innerHTML = "<li>Error fetching prediction data.</li>";
  }
});


// Load 3-month spending chart by category
async function loadSpendingChart() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/stats/category`);
    const data = await checkResponse(res);

    // data is expected to be array of { category: "...", total_spent: number }
    const labels = data.map(item => item.category);
    const values = data.map(item => item.total_spent);

    if (spendingChartInstance) spendingChartInstance.destroy();

    spendingChartInstance = new Chart(spendingChartCtx, {
      type: "doughnut",
      data: {
        labels,
        datasets: [{
          label: "Spending by Category (Last 3 Months)",
          data: values,
          backgroundColor: [
            "#FF6384",
            "#36A2EB",
            "#FFCE56",
            "#4BC0C0",
            "#9966FF",
            "#FF9F40",
            "#8A2BE2",
            "#00CED1",
            "#FF4500",
            "#9ACD32",
          ],
          borderWidth: 1,
        }],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: "right" },
          tooltip: {
            callbacks: {
              label: ctx => `${ctx.label}: ${ctx.parsed} BGN`
            }
          }
        }
      },
    });
  } catch (error) {
    console.error("Error loading spending chart:", error);
  }
}

// Logout handler
logoutButton.addEventListener("click", async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/logout`);
    if (res.ok) {
      window.location.href = `${API_BASE_URL}/login`;
    } else {
      alert("Logout failed");
    }
  } catch (err) {
    console.error("Logout error:", err);
  }
});

// Initial loading
loadTransactions();
loadSpendingChart();
