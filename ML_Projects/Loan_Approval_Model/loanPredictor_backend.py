
import joblib
import pandas as pd
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

import os
print(os.getcwd())

# ---------------------------------------------------------------------------
# Pydantic model — validates and documents every field the form sends.
# FastAPI uses this to auto-generate /docs (Swagger UI) for free.
# ---------------------------------------------------------------------------
class LoanApplication(BaseModel):
    Age: int                    = Field(..., ge=18,  le=100,  example=28)
    Gender: str                 = Field(...,                  example="female")
    Education: str              = Field(...,                  example="Bachelor")
    Person_Income: float        = Field(..., ge=0,            example=55000, alias="Person Income")
    Employee_Experience: int    = Field(..., ge=0,   le=60,   example=3,     alias="Employee Experience")
    Home_Onwership: str         = Field(...,                  example="RENT", alias="Home Onwership")
    Loan_Amount: float          = Field(..., ge=0,            example=12000, alias="Loan Amount")
    Loan_Intent: str            = Field(...,                  example="PERSONAL", alias="Loan Intent")
    Loan_interest_Rate: float   = Field(..., ge=0,   le=40,   example=11.5,  alias="Loan interest Rate")
    Loan_percentage: float      = Field(..., ge=0,   le=2,    example=0.22,  alias="Loan percentage")
    Credit_History: int         = Field(..., ge=0,            example=4,     alias="Credit History")
    Credit_Score: int           = Field(..., ge=300, le=900,  example=650,   alias="Credit Score")
    Previous_Loan: str          = Field(...,                  example="No",  alias="Previous Loan")

    model_config = {"populate_by_name": True}


# Column order the sklearn pipeline was trained on
EXPECTED_COLUMNS = [
    "Age",
    "Gender",
    "Education",
    "Person Income",
    "Employee Experience",
    "Home Onwership",
    "Loan Amount",
    "Loan Intent",
    "Loan interest Rate",
    "Loan percentage",
    "Credit History",
    "Credit Score",
    "Previous Loan",
]

# ---------------------------------------------------------------------------
# Lifespan: load model once at startup, clean up on shutdown
# ---------------------------------------------------------------------------
ml_pipeline = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    ml_pipeline["model"] = joblib.load("loan_model_pipeline.pkl")
    print("✓ Model loaded — ready to predict")
    yield
    ml_pipeline.clear()
    print("✓ Model unloaded — shutdown complete")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Loan Decision Desk",
    description="ML-powered loan approval predictor backed by a LightGBM pipeline.",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5501",
        "http://localhost:5501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (style.css, script.js) from the current directory
app.mount("/static", StaticFiles(directory="."), name="static")


@app.get("/", include_in_schema=False)
async def serve_index():
    """Serve the frontend HTML form."""
    return FileResponse("LoanPredictor.html")


@app.post("/predict")
async def predict(application: LoanApplication):
    """
    Run the loan application through the trained ML pipeline.

    Returns:
    - **prediction**: 1 = approved, 0 = declined
    - **probability_approved**: model confidence (0.0 – 1.0)
    """
    pipeline = ml_pipeline.get("model")
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet.")

    # Rebuild column names exactly as the pipeline expects (with spaces)
    row = {
        "Age": application.Age,
        "Gender": application.Gender,
        "Education": application.Education,
        "Person Income": application.Person_Income,
        "Employee Experience": application.Employee_Experience,
        "Home Onwership": application.Home_Onwership,
        "Loan Amount": application.Loan_Amount,
        "Loan Intent": application.Loan_Intent,
        "Loan interest Rate": application.Loan_interest_Rate,
        "Loan percentage": application.Loan_percentage,
        "Credit History": application.Credit_History,
        "Credit Score": application.Credit_Score,
        "Previous Loan": application.Previous_Loan,
    }

    df = pd.DataFrame([row], columns=EXPECTED_COLUMNS)

    prediction          = int(pipeline.predict(df)[0])
    probability_approved = float(pipeline.predict_proba(df)[0][1])

    return {
        "prediction": prediction,             # 1 = approved, 0 = declined
        "probability_approved": probability_approved,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)