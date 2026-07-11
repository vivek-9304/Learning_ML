const API_URL = "http://127.0.0.1:8000/predict";
 
const form = document.getElementById("loan-form");
const submitBtn = document.getElementById("submit-btn");
const resultBox = document.getElementById("result");
const errorBox = document.getElementById("error-box");
const stamp = document.getElementById("stamp");
const stampText = document.getElementById("stamp-text");
const decisionText = document.getElementById("decision-text");
const confidenceText = document.getElementById("confidence-text");
const refNumber = document.getElementById("ref-number");
 
// Give each page load a friendly reference number, purely cosmetic
refNumber.textContent = "Ref. #" + Math.floor(100000 + Math.random() * 900000);
 
// Fields that should be sent as numbers rather than strings
const NUMERIC_FIELDS = new Set([
  "Age",
  "Person Income",
  "Employee Experience",
  "Loan Amount",
  "Loan interest Rate",
  "Loan percentage",
  "Credit History",
  "Credit Score",
]);
 
form.addEventListener("submit", async (event) => {
  event.preventDefault();
 
  resultBox.hidden = true;
  errorBox.hidden = true;
 
  const formData = new FormData(form);
  const payload = {};
 
  for (const [key, value] of formData.entries()) {
    payload[key] = NUMERIC_FIELDS.has(key) ? Number(value) : value;
  }
 
  submitBtn.disabled = true;
  submitBtn.textContent = "Reviewing...";
 
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
 
    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }
 
    const data = await response.json();
    renderResult(data);
  } catch (err) {
    console.error(err);
    errorBox.hidden = false;
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Run underwriting";
  }
});
 
function renderResult(data) {
  // Expected shape from app.py:
  // { prediction: 0 | 1, probability_approved: 0.0-1.0 }
  const approved = data.prediction === 1;
  const probability = data.probability_approved;
 
  stamp.classList.toggle("is-declined", !approved);
  stampText.textContent = approved ? "Approved" : "Declined";
  decisionText.textContent = approved ? "Loan approved" : "Loan declined";
 
  const confidencePct = (
    approved ? probability : 1 - probability
  ) * 100;
  confidenceText.textContent = confidencePct.toFixed(1) + "%";
 
  resultBox.hidden = false;
  resultBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
}