# Business Problem

## Overview

Customer churn is a major challenge for subscription-based businesses.

When customers leave a service, companies lose recurring revenue and valuable relationships. 
Being able to identify customers with a high probability of churn allows businesses to take proactive retention actions.

This project aims to build an end-to-end Machine Learning platform that helps organizations understand customer behavior and predict churn risk.

---

## Business Goal

The goal of this project is to create a machine learning system that can:

- identify different customer segments using unsupervised learning
- predict customer churn probability using supervised learning
- provide insights into factors influencing churn predictions
- support data-driven customer retention decisions

---

## ML Problem Definition

This project contains two machine learning problems.

### 1. Customer Segmentation

Type:

Unsupervised Learning

Goal:

Discover natural groups of customers based on their characteristics and behavior.

Algorithm:

- KMeans clustering


Expected output:

Example customer segments:

- High-value customers
- New customers
- Price-sensitive customers
- High-risk customers


---

### 2. Churn Prediction

Type:

Supervised Learning - Classification

Goal:

Predict whether a customer is likely to leave the service.

Target variable:

`Churn`

Possible values:

- Yes
- No


Models to evaluate:

- Logistic Regression
- Random Forest
- XGBoost


---

## Expected Business Value

The system can help organizations:

- identify customers requiring attention
- prioritize retention activities
- understand customer behavior patterns
- improve decision-making using machine learning insights

---

## Project Scope

The project demonstrates a complete machine learning lifecycle:

1. Data preparation
2. Exploratory Data Analysis
3. Feature Engineering
4. Customer Segmentation
5. Churn Prediction
6. Experiment Tracking with MLflow
7. Model Deployment with FastAPI
8. Containerization with Docker
9. CI/CD automation
10. Basic monitoring

---

## Limitations

This project uses a public dataset.

In a real production environment, additional customer behavior data could improve predictions, for example:

- product usage frequency
- application activity
- support interactions
- customer satisfaction metrics
- engagement data