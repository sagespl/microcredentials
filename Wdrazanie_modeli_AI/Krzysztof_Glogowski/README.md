# document-classification
This is the project created to solve the task of clustering the documents (mainly invoices) based on their layout/structure.

# Project Structure
The project consists of the following subprojects:
- **invoice_generator**: This is the python application that generates the invoices that can be used as training and test data for the ML models.
- **ml_pipelines**: This is the project powered by Kedro framework that consists of the pipelines to preprocess the input pdfs, train the ML models and infer the clusters.
- **web_app**: This it the web application powered by FastApi that is used to provide the REST API for the clustering documents.

# Technologies:
- **Python**: The main programming language used in the project (in version 3.12).
- **uv**: The dependency management tool used to manage the project dependencies.
- **Jupyter Notebooks**: The tool used to create the notebooks for data analysis and exploration.
- **PyTorch**: The deep learning framework used to build the ML models.
- **Kedro**: The framework used to build the ML pipelines.
- **MLflow**: The tool used to track the experiments and manage the ML models.
- **FastAPI**: The web framework used to build the REST API for the ML models.
- **Docker**: The tool used to create the containers for the web application and ML flow server.
- **Kubernetes**: The orchestration tool used to deploy the web application and ML flow server.

# Getting Started

## Prerequisites
- Python 3.12
- uv 0.7.8
- pip
- Docker
- Kubernetes
- make command

## Installation
1. Clone the repository
2a. (Linux/McOS)Run the following command to install the dependencies:
   ```bash
   uv sync --no-group windows --extra cu126
   ```
   alternatively if you want to install pytorch without CUDA support, run:
   ```bash
   uv sync --no-group windows --extra cpu
   ```
2b. (Windows)Run the following command to install the dependencies:
   ```bash
   uv sync --all-groups --extra cu126
   ```
   alternatively if you want to install pytorch without CUDA support, run:
   ```bash
   uv sync --all-groups --extra cpu
   ```