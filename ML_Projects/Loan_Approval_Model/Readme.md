# 🏦 Loan Approval Prediction System

An end-to-end Machine Learning web application that predicts whether a loan application is likely to be **approved or rejected** based on applicant information.

The project demonstrates the complete ML deployment workflow—from data preprocessing and model training to backend API development and frontend integration.

---

## 📸 Preview

> Add screenshots here after deployment.

| Home Page | Prediction Result |
|-----------|-------------------|
| ![Home](images/home.png) | ![Result](images/result.png) |

---

# 🚀 Features

- Predicts loan approval in real time
- Clean and responsive web interface
- FastAPI backend
- Scikit-Learn preprocessing pipeline
- LightGBM Classifier
- Automatic categorical encoding
- Automatic feature scaling
- Probability score for prediction
- Input validation using Pydantic
- REST API support
- Interactive Swagger Documentation

---

# 🧠 Machine Learning Pipeline

The saved pipeline performs all preprocessing automatically.

```
Raw Input
      │
      ▼
ColumnTransformer
      │
      ├── StandardScaler
      │
      └── OneHotEncoder
      │
      ▼
LightGBM Classifier
      │
      ▼
Prediction
```

---

# 🛠 Tech Stack

### Machine Learning

- Python
- Pandas
- NumPy
- Scikit-Learn
- LightGBM
- Joblib

### Backend

- FastAPI
- Uvicorn
- Pydantic

### Frontend

- HTML5
- CSS3
- JavaScript

---

# 📂 Project Structure

```
Loan_Approval_Model/
│
├── loan_model_pipeline.pkl
├── loanPredictor_backend.py
├── LoanPredictor.html
├── style.css
├── script.js
├── loan_data_new.csv
├── loan_approval_predictor.ipynb
└── README.md
```

---

# 📊 Model Inputs

| Feature | Type |
|----------|------|
| Age | Integer |
| Gender | Category |
| Education | Category |
| Person Income | Float |
| Employee Experience | Integer |
| Home Ownership | Category |
| Loan Amount | Float |
| Loan Intent | Category |
| Loan Interest Rate | Float |
| Loan Percentage | Float |
| Credit History | Integer |
| Credit Score | Integer |
| Previous Loan | Category |

---

# 🎯 Model Output

Returns

- Loan Approved ✅
- Loan Rejected ❌

along with

- Approval Probability

Example

```json
{
    "prediction": 1,
    "probability_approved": 0.91
}
```

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/yourusername/Loan-Approval-Prediction.git
```

Move into the project directory

```bash
cd Loan-Approval-Prediction
```

Create virtual environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

Linux / Mac

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the Backend

```bash
uvicorn loanPredictor_backend:app --reload
```

Open

```
http://127.0.0.1:8000
```

Swagger API Documentation

```
http://127.0.0.1:8000/docs
```

---

# 🌐 API Endpoint

## POST

```
/predict
```

Example Request

```json
{
    "Age": 28,
    "Gender": "female",
    "Education": "Bachelor",
    "Person Income": 55000,
    "Employee Experience": 3,
    "Home Onwership": "RENT",
    "Loan Amount": 12000,
    "Loan Intent": "PERSONAL",
    "Loan interest Rate": 11.5,
    "Loan percentage": 0.22,
    "Credit History": 4,
    "Credit Score": 650,
    "Previous Loan": "No"
}
```

Example Response

```json
{
    "prediction": 1,
    "probability_approved": 0.87
}
```

---

# 🧩 Workflow

```
Dataset
   │
   ▼
Data Cleaning
   │
   ▼
Feature Engineering
   │
   ▼
Preprocessing Pipeline
   │
   ▼
LightGBM Training
   │
   ▼
Save Model (.pkl)
   │
   ▼
FastAPI Backend
   │
   ▼
REST API
   │
   ▼
Frontend
   │
   ▼
Prediction
```

---

# 📌 Future Improvements

- User authentication
- Database integration
- Docker support
- Cloud deployment (Render/AWS/Azure)
- Batch prediction
- Prediction history
- Explainable AI (SHAP)
- Dark mode
- Model monitoring

---

# 👨‍💻 Author

**Titan**

B.Tech CSE (AI & ML)

Passionate about Machine Learning, Deep Learning, Backend Development and AI Systems.

---

# ⭐ If you like this project

Give this repository a ⭐ on GitHub.