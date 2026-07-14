import pandas as pd
import numpy as np

def generate_data(filename="telecom_churn.csv", num_records=10000):
    np.random.seed(42)
    
    data = {
        'SeniorCitizen': np.random.choice([0, 1], size=num_records, p=[0.8, 0.2]),
        'tenure': np.random.randint(1, 73, size=num_records),
        'MonthlyCharges': np.random.uniform(18.25, 118.75, size=num_records),
        'TotalCharges': np.random.uniform(18.25, 8000.00, size=num_records),
        'gender_Male': np.random.choice([0, 1], size=num_records),
        'Partner_Yes': np.random.choice([0, 1], size=num_records),
        'Dependents_Yes': np.random.choice([0, 1], size=num_records),
        'PhoneService_Yes': np.random.choice([0, 1], size=num_records, p=[0.1, 0.9]),
        'MultipleLines_No phone service': np.random.choice([0, 1], size=num_records, p=[0.9, 0.1]),
        'MultipleLines_Yes': np.random.choice([0, 1], size=num_records),
        'InternetService_Fiber optic': np.random.choice([0, 1], size=num_records, p=[0.4, 0.6]),
        'InternetService_No': np.random.choice([0, 1], size=num_records, p=[0.2, 0.8]),
        'OnlineSecurity_Yes': np.random.choice([0, 1], size=num_records),
        'OnlineBackup_Yes': np.random.choice([0, 1], size=num_records),
        'DeviceProtection_Yes': np.random.choice([0, 1], size=num_records),
        'TechSupport_Yes': np.random.choice([0, 1], size=num_records),
        'StreamingTV_Yes': np.random.choice([0, 1], size=num_records),
        'StreamingMovies_Yes': np.random.choice([0, 1], size=num_records),
        'Contract_One year': np.random.choice([0, 1], size=num_records, p=[0.2, 0.8]),
        'Contract_Two year': np.random.choice([0, 1], size=num_records, p=[0.3, 0.7]),
        'PaperlessBilling_Yes': np.random.choice([0, 1], size=num_records),
        'PaymentMethod_Credit card (automatic)': np.random.choice([0, 1], size=num_records),
        'PaymentMethod_Electronic check': np.random.choice([0, 1], size=num_records),
        'PaymentMethod_Mailed check': np.random.choice([0, 1], size=num_records),
        'customer_notes': [f"Customer has issues with bills." if x > 0.7 else "No issues reported." for x in np.random.rand(num_records)]
    }
    
    df = pd.DataFrame(data)
    
    # Calculate synthetic churn base target matching high monthly fees / low tenure profiles
    churn_prob = 1 / (1 + np.exp(-(-2.0 + 0.03 * df['MonthlyCharges'] - 0.04 * df['tenure'] + 0.5 * df['InternetService_Fiber optic'])))
    df['Churn'] = [1 if x > np.random.rand() else 0 for x in churn_prob]
    
    df.to_csv(filename, index=False)
    print(f" Successfully generated raw data skeleton asset: {filename}")

if __name__ == "__main__":
    generate_data()