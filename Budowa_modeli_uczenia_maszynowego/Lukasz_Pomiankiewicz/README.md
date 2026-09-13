# Customer Intelligence ML Platform

An end-to-end Machine Learning platform for customer churn prediction and customer segmentation, built with a production-oriented ML engineering workflow.

The project combines supervised and unsupervised learning with experiment tracking, model registry, explainability, API serving, containerization, automated testing, and CI/CD.

## Overview

The platform answers two complementary questions:

1. **Which customers are most likely to churn?**
2. **What types of customers exist within the customer base?**

The churn model is a Logistic Regression model selected as the **Champion Model** and registered in MLflow. Customer segmentation is performed using KMeans clustering.

The platform also uses SHAP to explain predictions at three levels:

* global model explainability
* segment-specific explainability
* local explanations for individual customers

## Architecture

```text
                         Customer Data
                              │
                              ▼
                   Validation & Preprocessing
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
        Churn Prediction            Customer Segmentation
                 │                         │
       Logistic Regression              KMeans
          Champion v1                    K = 4
                 │                         │
                 ▼                         ▼
          MLflow Registry          Segment Profiles
                 │                         │
                 └────────────┬────────────┘
                              │
                              ▼
                       SHAP Explainability
                    ┌─────────┼─────────┐
                    │         │         │
                  Global   Segment     Local
                              │
                              ▼
                           FastAPI
                              │
                              ▼
                            Docker
                              │
                              ▼
                       GitHub Actions
```

## Machine Learning

### Churn Prediction

Several supervised learning approaches were evaluated, including:

* Logistic Regression
* Random Forest
* XGBoost

The project uses **ROC-AUC as the primary model comparison metric**, with precision, recall and F1 used as supporting metrics.

The final Champion Model registered in MLflow is:

**Logistic Regression — `customer-churn-model` v1**

The Champion achieved approximately:

| Metric    | Score |
| --------- | ----: |
| Accuracy  | 0.805 |
| Precision | 0.658 |
| Recall    | 0.553 |
| F1        | 0.601 |
| ROC-AUC   | 0.845 |

The model is stored as an end-to-end scikit-learn pipeline containing both preprocessing and the classifier.

### Customer Segmentation

Customer segmentation uses KMeans clustering.

Silhouette scores were evaluated for `K = 2` through `K = 6`:

| Clusters | Silhouette |
| -------: | ---------: |
|        2 |     0.2837 |
|        3 |     0.2619 |
|    **4** | **0.2935** |
|        5 |     0.2721 |
|        6 |     0.2898 |

`K = 4` was selected.

The resulting segments are:

| Segment | Name                | Customers | Churn Rate | Avg. Tenure | Avg. Monthly Charges |
| ------: | ------------------- | --------: | ---------: | ----------: | -------------------: |
|       0 | Loyal High-Value    |     1,813 |      12.6% |        58.8 |                88.39 |
|       1 | New At-Risk         |     2,491 |      42.1% |        14.1 |                68.67 |
|       2 | Established At-Risk |     1,110 |      42.8% |        32.4 |                79.40 |
|       3 | Low-Cost Stable     |     1,629 |       7.2% |        30.9 |                22.52 |

The segment names are business-oriented interpretations of the resulting clusters rather than labels produced directly by KMeans.

## Explainability with SHAP

SHAP is used to understand why the Champion model produces its predictions.

### Global explainability

Across the full customer population, the most influential features are:

| Feature                         | Mean absolute SHAP |
| ------------------------------- | -----------------: |
| `tenure`                        |              1.113 |
| `MonthlyCharges`                |              0.518 |
| `TotalCharges`                  |              0.434 |
| `InternetService = Fiber optic` |              0.318 |
| `Contract = Two year`           |              0.292 |
| `Contract = Month-to-month`     |              0.287 |

### Segment-specific explainability

SHAP values are also calculated separately for each KMeans segment using the same Champion model.

This makes it possible to answer questions such as:

* Which factors are most important for high-risk customer groups?
* Does the direction of a feature's influence differ between segments?
* Which segments appear to be driven by tenure, pricing, contract type, or internet service?

For example, `tenure` is strongly associated with lower churn risk in the Loyal High-Value segment, while it is strongly associated with higher predicted churn risk in the New At-Risk segment.

### Local explainability

For an individual prediction, the API returns the strongest SHAP factors contributing to the prediction.

Example:

```json
{
  "feature": "tenure",
  "impact": "increases_churn",
  "shap_value": 1.627
}
```

Positive SHAP values move the model output toward churn, while negative values move it away from churn.

SHAP values describe model behaviour and should not be interpreted as causal effects.

## API

The FastAPI service exposes:

### Health check

```http
GET /health
```

### Churn prediction

```http
POST /predict
```

The endpoint returns:

```json
{
  "churn_prediction": 1,
  "churn_probability": 0.6928,
  "segment": 1,
  "segment_name": "New At-Risk",
  "top_factors": [
    {
      "feature": "tenure",
      "impact": "increases_churn",
      "shap_value": 1.627
    },
    {
      "feature": "TotalCharges",
      "impact": "decreases_churn",
      "shap_value": -0.500
    },
    {
      "feature": "InternetService = Fiber optic",
      "impact": "increases_churn",
      "shap_value": 0.333
    }
  ]
}
```

The API therefore combines:

* churn prediction
* churn probability
* customer segment
* human-readable segment name
* local SHAP explanation

## MLflow

MLflow is used for:

* experiment tracking
* metric logging
* model artifacts
* model registry
* loading registered models for serving

Registered models:

```text
customer-churn-model
└── v1 — Champion Logistic Regression

customer-segmentation-model
└── v1 — KMeans
```

The application loads models from the MLflow Model Registry instead of retraining them during API startup.

## Engineering Practices

The project demonstrates several ML Engineering practices:

* reproducible Python environment with `uv`
* modular project structure
* reusable preprocessing pipelines
* experiment tracking with MLflow
* model registry
* model serving with FastAPI
* Docker containerization
* automated testing with pytest
* code quality checks with Ruff
* CI/CD with GitHub Actions

## Testing

The project includes automated tests for:

* FastAPI health endpoint
* churn prediction endpoint
* prediction response structure
* SHAP factor filtering
* KMeans segmentation
* segment profiling

Current test suite:

```text
4 passed
```

Ruff:

```text
All checks passed!
```

## Project Structure

```text
customer-intelligence-ml-platform/
│
├── data/
│   └── raw/
│
├── src/
│   ├── api/
│   │   ├── main.py
│   │   └── schemas.py
│   │
│   ├── data/
│   │   └── load_data.py
│   │
│   ├── features/
│   │   ├── encoding.py
│   │   └── preprocessing.py
│   │
│   ├── models/
│   │   ├── load_model.py
│   │   └── load_segmenter.py
│   │
│   ├── pipelines/
│   │   └── churn_pipeline.py
│   │
│   ├── segmentation/
│   │   ├── kmeans.py
│   │   ├── profiling.py
│   │   └── run_segmentation.py
│   │
│   ├── explainability/
│   │   ├── shap_explainer.py
│   │   └── segment_explanation.py
│   │
│   └── training/
│       └── train_model.py
│
├── tests/
│   ├── test_api.py
│   └── test_segmentation.py
│
├── Dockerfile
├── pyproject.toml
├── uv.lock
└── README.md
```

## Tech Stack

* Python 3.12
* uv
* pandas
* NumPy
* scikit-learn
* XGBoost
* SHAP
* MLflow
* FastAPI
* Pydantic
* Docker
* pytest
* Ruff
* GitHub Actions

## Running Locally

Install dependencies:

```bash
uv sync
```

Activate the virtual environment on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Start the MLflow server:

```powershell
mlflow server --host 0.0.0.0 --port 5001 --workers 1 --allowed-hosts "localhost:*,host.docker.internal:*"
```

In another terminal:

```powershell
$env:MLFLOW_TRACKING_URI="http://localhost:5001"
```

Run the segmentation pipeline:

```powershell
uv run python -m src.segmentation.run_segmentation
```

Run the API:

```powershell
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

API documentation is then available at:

```text
http://localhost:8000/docs
```

Run tests:

```powershell
uv run pytest
```

Run Ruff:

```powershell
uv run ruff check .
```

## CI/CD

GitHub Actions automatically validates the project on push by running the automated test and code-quality checks.

The repository is also configured to build and publish the application container.

## Project Goal

This project was built as a practical demonstration of an end-to-end ML Engineering workflow rather than as a competition-oriented model.

The emphasis is on connecting the individual components:

```text
data
→ preprocessing
→ modelling
→ experiment tracking
→ model registry
→ segmentation
→ explainability
→ API serving
→ containerization
→ CI/CD
```

The result is a small but complete ML platform that can be extended with additional models, monitoring, cloud deployment, or a user interface in future iterations.
