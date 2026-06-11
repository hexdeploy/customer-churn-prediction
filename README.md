# 📊 End-to-End Customer Churn Prediction System

A production-ready Machine Learning system that predicts customer churn risk using customer demographics and account details. This project transitions from an experimental Jupyter Notebook into a containerized microservice deployed in the cloud, paired with an interactive user dashboard.

## 🚀 Live Demo & Interfaces
* **Interactive User Interface:** Run `ui.py` locally to launch the Streamlit dashboard.
* **Cloud API Documentation (Swagger UI):** **[👉 Test the Live API Here](https://customer-churn-prediction-api-1.onrender.com/docs)**

---

## 🛠️ System Architecture & Evolution

### 🔹 Level 1: Modularization & API Architecture
* **Robust Preprocessing:** Handled non-numeric IDs, handled missing properties, and implemented One-Hot Encoding to prevent production inference data alignment errors.
* **Class Imbalance Correction:** Integrated native training balance weights (`class_weight='balanced'`) to optimize for true recall metrics.
* **FastAPI Microservice:** Developed an asynchronous local web engine endpoint (`app.py`) for instantaneous inference.

### 🔹 Level 2: Cloud Containerization & DevOps Deployment
* **Docker Isolation:** Created a standardized multi-step `Dockerfile` to guarantee reproducibility across development and production servers using `python:3.11-slim`.
* **CI/CD Cloud Pipelines:** Automated Git-triggered cloud deployment builds directly linked to **Render** infrastructure.

### 🔹 Level 3: Interactive Frontend Dashboard
* **Streamlit UI:** Built a clean, user-friendly graphical interface (`ui.py`) featuring side-by-side demographic forms, input sliders, and immediate color-coded risk alerts.
* **API Integration:** Configured asynchronous `requests` communication to securely pass UI payloads to the live cloud server, isolating true churn probability indices (`Class 1`).

---

## ⚙️ How to Run the Interface Locally

To launch the interactive dashboard on your machine while connecting to the live Render cloud engine, follow these steps:

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git)
   cd YOUR_REPO_NAME

Install Dependencies:
pip install streamlit requests pandas scikit-learn joblib 

Launch the Streamlit App:
streamlit run ui.py

💻 Technical Stack
Languages: Python 3.11
Machine Learning: Scikit-Learn, Pandas, NumPy, Joblib
API Framework: FastAPI, Uvicorn, Pydantic
User Interface: Streamlit Framework
DevOps: Docker, Git, GitHub, Render Infrastructure Cloud 

> ⚠️ **Important:** Don't forget to replace `YOUR_ACTUAL_RENDER_URL`, `YOUR_GITHUB_USERNAME`, and `YOUR_REPO_NAME` inside that file with your actual project links so they work perfectly!