const API_URL = "http://localhost:5000/transactions";

const form = document.getElementById("transactionForm");
const list = document.getElementById("transactionList");
const predictionText = document.getElementById("prediction");

async function loadTransactions() {
  const res = await fetch(API_URL);
  const data = await res.json();

  list.innerHTML = "";

  data.reverse().forEach((t) => {
    const item = document.createElement("li");
    item.className = t.type === "income" ? "income" : "";
    item.innerText = `${t.date} — ${t.description} — ${t.amount.toFixed(2)} BGN [${t.category}] (${t.type})`;
    list.appendChild(item);
  });
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const amount = parseFloat(document.getElementById("amount").value);
  const description = document.getElementById("description").value;
  const date = document.getElementById("date").value;
  const type = document.querySelector('input[name="type"]:checked').value;

  if (!description || isNaN(amount) || !date) return;

  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ amount, description, date, type }),
  });

  const data = await res.json();
  predictionText.innerText = `Predicted category: ${data.category}`;
  form.reset();
  loadTransactions();
});

loadTransactions();

const predictBtn = document.getElementById("predictButton");
const forecastList = document.getElementById("forecastList");

predictBtn.addEventListener("click", async () => {
  const res = await fetch("http://localhost:5000/predict");
  const data = await res.json();

  forecastList.innerHTML = "";

  const { forecast, total_income, total_spending, net_savings } = data;

  // Summary display
  const summary = document.createElement("li");
  summary.innerHTML = `
    <strong>💰 Forecast Summary:</strong><br>
    Expected Income: <b>${total_income.toFixed(2)} BGN</b><br>
    Expected Spending: <b>${total_spending.toFixed(2)} BGN</b><br>
    Estimated Savings: <b>${net_savings.toFixed(2)} BGN</b>
  `;
  forecastList.appendChild(summary);

  forecast.forEach((item) => {
    const li = document.createElement("li");
    li.innerText = `${item.date} — ${item.description}: ${item.amount.toFixed(2)} BGN (${item.type})`;
    forecastList.appendChild(li);
  });

  if (forecast.length === 0) {
    forecastList.innerHTML += `<li>No predictable transactions for next month yet.</li>`;
  }
});

