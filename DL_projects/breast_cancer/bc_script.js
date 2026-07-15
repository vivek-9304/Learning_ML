const API_BASE = "http://127.0.0.1:8000";
 
const form = document.getElementById("prognosisForm");
const submitBtn = document.getElementById("submitBtn");
const formHint = document.getElementById("formHint");
 
const resultEmpty = document.getElementById("resultEmpty");
const resultContent = document.getElementById("resultContent");
const resultLabel = document.getElementById("resultLabel");
const confidenceFill = document.getElementById("confidenceFill");
const confidenceText = document.getElementById("confidenceText");
 
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  formHint.textContent = "";
 
  const formData = new FormData(form);
 
  // Build the payload with the exact keys the API expects.
  const payload = {
    Age: Number(formData.get("Age")),
    Race: formData.get("Race"),
    "Marital Status": formData.get("Marital Status"),
    "T Stage": formData.get("T Stage"),
    "N Stage": formData.get("N Stage"),
    "6th Stage": formData.get("6th Stage"),
    differentiate: formData.get("differentiate"),
    Grade: formData.get("Grade"),
    "A Stage": formData.get("A Stage"),
    "Tumor Size": Number(formData.get("Tumor Size")),
    "Estrogen Status": formData.get("Estrogen Status"),
    "Progesterone Status": formData.get("Progesterone Status"),
    "Regional Node Examined": Number(formData.get("Regional Node Examined")),
    "Reginol Node Positive": Number(formData.get("Reginol Node Positive")),
    "Survival Months": Number(formData.get("Survival Months")),
  };
 
  setLoading(true);
 
  try {
    const res = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
 
    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new Error(errBody.detail || `Server responded with ${res.status}`);
    }
 
    const data = await res.json();
    renderResult(data);
  } catch (err) {
    formHint.textContent = `Couldn't reach the model: ${err.message}`;
  } finally {
    setLoading(false);
  }
});
 
function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  submitBtn.classList.toggle("loading", isLoading);
  submitBtn.querySelector(".btn-label").textContent = isLoading
    ? "Reading…"
    : "Read the chart";
}
 
function renderResult(data) {
  // Expected shape: { prediction: "Alive" | "Dead", probability: 0.0-1.0 }
  const prediction = data.prediction ?? "Unknown";
  const probability = typeof data.probability === "number" ? data.probability : null;
 
  resultEmpty.hidden = true;
  resultContent.hidden = false;
 
  resultLabel.textContent = prediction;
  resultLabel.classList.remove("outcome-good", "outcome-caution");
  resultLabel.classList.add(
    prediction.toLowerCase() === "alive" ? "outcome-good" : "outcome-caution"
  );
 
  if (probability !== null) {
    const pct = Math.round(probability * 100);
    requestAnimationFrame(() => {
      confidenceFill.style.width = `${pct}%`;
    });
    confidenceText.textContent = `Model confidence: ${pct}%`;
  } else {
    confidenceFill.style.width = "0%";
    confidenceText.textContent = "Model confidence unavailable";
  }
}