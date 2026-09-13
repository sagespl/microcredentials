from pydantic import BaseModel


class CustomerData(BaseModel):
    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str
    tenure: int
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: float


class PredictionFactor(BaseModel):
    feature: str
    impact: str
    shap_value: float


class PredictionResponse(BaseModel):
    churn_prediction: int
    churn_probability: float
    segment: int
    segment_name: str
    top_factors: list[PredictionFactor]