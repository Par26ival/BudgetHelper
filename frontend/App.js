const API_BASE_URL = "http://localhost:5000";

const form = document.getElementById("transactionForm");
const list = document.getElementById("transactionList");
const predictionText = document.getElementById("prediction");
const predictBtn = document.getElementById("predictButton");
const forecastList = document.getElementById("forecastList");
const logoutButton = document.getElementById("logoutButton");

// Default fetch options with credentials
const defaultFetchOptions = {
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
};

// Get current user information
async function getCurrentUser() {
  try {
    const response = await fetch(`${API_BASE_URL}/transactions`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include"
    });

    if (!response.ok) {
      if (response.status === 401) {
        window.location.href = "/login";
        return;
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Get user info from the response headers
    const userInfo = response.headers.get('X-User-Info');
    if (userInfo) {
      const user = JSON.parse(userInfo);
      const headerTitle = document.querySelector('header h1');
      headerTitle.innerHTML = `💳 BudgetHelper - ${user.username}`;
    }
  } catch (error) {
    console.error("Error getting user info:", error);
  }
}

// Handle unauthorized responses
async function handleResponse(response) {
  if (response.status === 401) {
    // Session expired or unauthorized
    window.location.href = "/login";
    return null;
  }
  return response;
}

// Load and display transactions
async function loadTransactions() {
  try {
    const response = await fetch(`${API_BASE_URL}/transactions`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include"
    });

    const handledResponse = await handleResponse(response);
    if (!handledResponse) return;

    const transactions = await handledResponse.json();
    const transactionList = document.getElementById("transactionList");
    transactionList.innerHTML = "";

    if (transactions.length === 0) {
      transactionList.innerHTML = `
        <div class="empty-state">
          <p>No transactions found. Add your first transaction!</p>
        </div>`;
      return;
    }

    transactions.forEach((transaction) => {
      const row = document.createElement("tr");
      row.className = `transaction-row ${transaction.type}`;
      const amount = Math.abs(transaction.amount).toFixed(2);
      const date = new Date(transaction.date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });

      row.innerHTML = `
        <td class="transaction-description">
          <span class="description">${transaction.description}</span>
          <span class="category">${transaction.category || "Uncategorized"}</span>
        </td>
        <td class="transaction-amount ${transaction.type}">
          ${transaction.type === "income" ? "+" : "-"}$${amount}
        </td>
        <td class="transaction-date">${date}</td>
      `;
      transactionList.appendChild(row);
    });
  } catch (error) {
    console.error("Error loading transactions:", error);
    const transactionList = document.getElementById("transactionList");
    transactionList.innerHTML = `
      <div class="error-state">
        <p>Error loading transactions. Please try again.</p>
      </div>`;
  }
}

// Handle new transaction submission
form.addEventListener("submit", async e => {
  e.preventDefault();

  const amount = parseFloat(document.getElementById("amount").value);
  const description = document.getElementById("description").value.trim();
  const date = document.getElementById("date").value;
  const type = document.querySelector('input[name="type"]:checked').value;

  if (!description || isNaN(amount) || !date) return;

  try {
    const res = await fetch(`${API_BASE_URL}/transactions`, {
      ...defaultFetchOptions,
      method: "POST",
      body: JSON.stringify({ amount, description, date, type })
    });

    const handledResponse = await handleResponse(res);
    if (!handledResponse) return;

    const data = await handledResponse.json();
    predictionText.textContent = `Predicted category: ${data.category}`;
    form.reset();
    loadTransactions();
  } catch (error) {
    console.error("Error submitting transaction:", error);
    predictionText.textContent = "Error adding transaction";
  }
});

// Add event listener for predict button
document.addEventListener('DOMContentLoaded', function () {
  const predictButton = document.getElementById('predictButton');
  if (predictButton) {
    predictButton.addEventListener('click', getPrediction);
  } else {
    console.error('Predict button not found');
  }
});

async function getPrediction() {
  try {
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "include"
    });

    const handledResponse = await handleResponse(response);
    if (!handledResponse) return;

    const data = await handledResponse.json();
    const forecastList = document.getElementById("forecastList");
    if (!forecastList) return;
    forecastList.innerHTML = "";

    // Only show prediction
    const predictions = document.createElement("li");
    predictions.innerHTML = `
        <strong>💰 Predictions (Next 30 Days):</strong><br>
        Predicted Income: <b>${data.predicted_income.toFixed(2)} BGN</b><br>
        Predicted Spending: <b>${data.predicted_spending.toFixed(2)} BGN</b>
    `;
    forecastList.appendChild(predictions);

    // Add category breakdown
    if (data.spending_by_category && Object.keys(data.spending_by_category).length > 0) {
      const categoryHeader = document.createElement("li");
      categoryHeader.innerHTML = "<strong>Spending by Category:</strong>";
      forecastList.appendChild(categoryHeader);

      Object.entries(data.spending_by_category).forEach(([category, amount]) => {
        const li = document.createElement("li");
        li.innerText = `${category}: ${amount.toFixed(2)} BGN`;
        forecastList.appendChild(li);
      });
    }
  } catch (error) {
    console.error("Error fetching prediction:", error);
    const forecastList = document.getElementById("forecastList");
    if (forecastList) {
      forecastList.innerHTML = "<li>Error loading predictions</li>";
    }
  }
}

// Logout handler
logoutButton.addEventListener("click", async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/logout`, defaultFetchOptions);
    const data = await res.json();
    if (res.ok) {
      window.location.href = data.redirect;
    } else {
      alert("Logout failed");
    }
  } catch (err) {
    console.error("Logout error:", err);
    // If there's an error, still try to redirect to login
    window.location.href = `${API_BASE_URL}/login`;
  }
});

// Initial loading
getCurrentUser();
loadTransactions();
