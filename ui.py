import streamlit as st
import requests

# 1. Set up the web page title and design layout
st.set_page_config(page_title="Customer Churn Predictor", page_icon="📊", layout="centered")

st.title("📊 Customer Churn Risk Predictor")
st.write("Enter the customer's details below to analyze their risk of leaving the service.")

st.markdown("---")

# 2. Create the input forms in nice side-by-side columns
col1, col2 = st.columns(2)

with col1:
    gender = st.selectbox("Gender", ["Male", "Female"])
    senior = st.selectbox("Senior Citizen?", ["No", "Yes"])
    partner = st.selectbox("Has a Partner?", ["No", "Yes"])
    dependents = st.selectbox("Has Dependents?", ["No", "Yes"])
    tenure = st.number_input("Tenure (Months with company)", min_value=0, max_value=100, value=12)
    phone_service = st.selectbox("Phone Service?", ["Yes", "No"])
    multiple_lines = st.selectbox("Multiple Lines?", ["No", "Yes", "No phone service"])
    internet_service = st.selectbox("Internet Service Type", ["Fiber optic", "DSL", "No"])

with col2:
    security = st.selectbox("Online Security Add-on?", ["No", "Yes", "No internet service"])
    backup = st.selectbox("Online Backup Add-on?", ["No", "Yes", "No internet service"])
    protection = st.selectbox("Device Protection Add-on?", ["No", "Yes", "No internet service"])
    support = st.selectbox("Tech Support Add-on?", ["No", "Yes", "No internet service"])
    tv = st.selectbox("Streaming TV?", ["No", "Yes", "No internet service"])
    movies = st.selectbox("Streaming Movies?", ["No", "Yes", "No internet service"])
    contract = st.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"])
    paperless = st.selectbox("Paperless Billing?", ["Yes", "No"])
    payment = st.selectbox("Payment Method", ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"])

monthly_charges = st.slider("Monthly Charges ($)", min_value=10.0, max_value=150.0, value=65.0)
total_charges = st.number_input("Total Charges ($)", min_value=0.0, max_value=10000.0, value=500.0)

st.markdown("---")

# 3. Handle the prediction transmission when the button is clicked
if st.button("🔍 Analyze Customer Churn Risk", use_container_width=True):
    
    # Map friendly UI inputs back to what our API expects (0 and 1 for senior)
    senior_numeric = 1 if senior == "Yes" else 0
    
    # Construct the JSON payload exactly like our API expects
    payload = {
        "gender": gender,
        "SeniorCitizen": senior_numeric,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": int(tenure),
        "PhoneService": phone_service,
        "MultipleLines": multiple_lines,
        "InternetService": internet_service,
        "OnlineSecurity": security,
        "OnlineBackup": backup,
        "DeviceProtection": protection,
        "TechSupport": support,
        "StreamingTV": tv,
        "StreamingMovies": movies,
        "Contract": contract,
        "PaperlessBilling": paperless,
        "PaymentMethod": payment,
        "MonthlyCharges": float(monthly_charges),
        "TotalCharges": float(total_charges)
    }
    
    # REPLACE THIS URL WITH YOUR ACTUAL LIVE RENDER API LINK!
    # Make sure to leave /predict at the end of it
    API_URL = "https://customer-churn-prediction-api-1.onrender.com/predict"
    
    try:
        with st.spinner("Communicating with live cloud model... Please wait..."):
            response = requests.post(API_URL, json=payload)
            
        if response.status_code == 200:
            result = response.json()
            probability = result["churn_probability_percentage"]
            prediction = result["churn_prediction"]
            
            # Display results beautifully based on risk severity
            st.subheader("Analysis Results:")
            if prediction == 1:
                st.error(f"⚠️ **High Risk of Churn!** The model predicts this customer is likely to leave.")
                st.metric(label="Churn Probability", value=f"{probability:.2f}%")
            else:
                st.success(f"✅ **Low Risk Customer.** The model predicts this customer will likely stay loyal.")
                st.metric(label="Churn Probability", value=f"{probability:.2f}%")
        else:
            st.error(f"Error: API returned status code {response.status_code}")
            
    except Exception as e:
        st.error(f"Could not connect to the cloud API server. Check your URL. Error: {e}")