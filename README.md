# 🔮 Customer Churn Prediction Pipeline & Dashboard

[![Vercel Deployment](https://img.shields.io/badge/Frontend-Vercel-black?style=flat-square&logo=vercel)](https://customer-churn-prediction-kappa-eight.vercel.app/)
[![Render Deployment](https://img.shields.io/badge/Backend-Render-46E3B7?style=flat-square&logo=render&logoColor=white)](https://customer-churn-prediction-1k4a.onrender.com)
[![Database](https://img.shields.io/badge/Database-MongoDB_Atlas-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://cloud.mongodb.com/)
[![Tech Stack](https://img.shields.io/badge/Stack-FastAPI_%7C_React_%7C_Python-blue?style=flat-square)](#)

An end-to-end, live cloud-synchronized machine learning pipeline that predicts customer churn, analyzes customer sentiment from raw textual notes, and logs incoming evaluations to **MongoDB Atlas**. This repository features a high-performance **FastAPI** backend and an interactive, beautifully tailored **React** administrative control center.

---

## 🚀 Live Production Links
*   **Web App (UI):** [Customer Churn Prediction (Vercel)](https://customer-churn-system.vercel.app/)

---

## ✨ Features

### 1. 🧠 Predictive Inference Engine (FastAPI)
*   Computes real-time **Churn Probability** using customer attributes (Tenure, Monthly Charges, Senior Citizen Status).
*   Performs NLP-driven sentiment extraction on unstructured service notes to enrich churn forecasting.
*   Classifies risk categorization into structured labels: `High Risk`, `Moderate Risk`, and `Low Risk`.

### 2. 📊 Live Analytical Dashboard (React)
*   **Visual KPIs:** Displays aggregate metrics including total evaluated runs, risk tier percentages, and live server latency/pipeline health status.
*   **Interactive Search & Filters:** Instantly search by exact **Customer ID** or filter the live records by risk verdicts using memory-optimized frontend caching.
*   **Local Timezone Mapping:** Automatically reformats incoming UTC timestamps to match the administrator's local system clock.
*   **Dynamic Logs Management:** Features an on-the-fly **Delete** mechanism that safely dispatches removal requests to the MongoDB Atlas backend cluster and instantly updates the UI state.

---

## 📐 System Architecture

```
                  ┌─────────────────────────────────┐
                  │          React Frontend         │
                  │        (Hosted on Vercel)       │
                  └────────────────┬────────────────┘
                                   │
                    HTTPS Requests │ API Endpoints
                                   ▼
                  ┌─────────────────────────────────┐
                  │         FastAPI Backend         │
                  │        (Hosted on Render)       │
                  └────────────────┬────────────────┘
                                   │
                PyMongo Connection │ Drivers
                                   ▼
                  ┌─────────────────────────────────┐
                  │       MongoDB Atlas Cloud       │
                  │      (Replica Set Cluster)      │
                  └─────────────────────────────────┘
```

---

## 🛠️ Tech Stack

*   **Frontend:** React (Vite), Modern CSS3, HTML5, Local Storage state preservation.
*   **Backend:** Python 3.10+, FastAPI (ASGI Framework), Uvicorn, Pydantic (Data validation).
*   **Database:** MongoDB Atlas (NoSQL cloud cluster), PyMongo Driver.
*   **Deployment:** Vercel (Frontend CD), Render (Backend CD with automated container build pipelines).

---

## 📂 Project Repository Directory Tree

```text
customer-churn-prediction/
├── frontend/                   # React web application
│   ├── public/
│   │   └── logo.png            # Custom application tab brand mark
│   ├── src/
│   │   ├── App.jsx             # Main interactive dashboard code (States, API Fetch, Table)
│   │   └── main.jsx            # Application mount configuration
│   ├── index.html              # Custom SEO settings & favicon pointer
│   └── package.json
└── backend/                    # Python API Service
    ├── main.py                 # FastAPI endpoints, CORS, database connectivity
    ├── requirements.txt        # Production dependencies
    └── .env                    # Environment credentials (MONGO_URI)
```

---

## ⚙️ Local Configuration & Setup

### 1. Backend Setup
Clone the repository and access your backend directory:
```bash
cd backend
```

Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install the project dependencies:
```bash
pip install -r requirements.txt
```

Create a `.env` file and insert your Mongo URI connection string:
```env
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/churn-database?retryWrites=true&w=majority
```

Boot the server locally:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

### 2. Frontend Setup
Navigate into the frontend workspace:
```bash
cd ../frontend
```

Install local node modules:
```bash
npm install
```

Start the Vite development server:
```bash
npm run dev
```
Your local server will spin up on `http://localhost:5173`. Update `API_BASE_URL` in `App.jsx` if linking to your local FastAPI backend instance!

---

## 📡 API Endpoints Documentation

| Method | Endpoint | Description | Payload Schema |
| :--- | :--- | :--- | :--- |
| **POST** | `/predict` | Processes single customer telemetry, runs predictive algorithms, and commits record directly to Atlas. | `{ customer_id: string, tenure: int, monthly_charges: float, senior_citizen: int, notes: string }` |
| **GET** | `/history` | Fetches the complete, raw array of historic pipeline predictions logged inside the Atlas collection. | *None* |
| **GET** | `/metrics` | Computes live operational statuses, active volumes, and risk breakdown statistics. | *None* |
| **DELETE** | `/history/{id}`| Removes the specified customer log from the MongoDB database collection permanently. | *Path Parameter: customer_id* |

---

## 🧪 Clean Database & Auto-recreation
If you ever need to purge database rows for troubleshooting or testing purposes:
1. Log into **[MongoDB Atlas](https://cloud.mongodb.com)**.
2. Select **Browse Collections** -> Locate your collection -> Click **Drop Collection** or hit the **Trash** icon.
3. Your FastAPI backend will automatically construct a clean collection automatically on the next evaluation event!

---

## 🛡️ License
Distributed under the MIT License. See `LICENSE` for further details.
