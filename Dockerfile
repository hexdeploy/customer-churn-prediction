# Step 1: Use an official lightweight Python runtime as a parent image
FROM python:3.11-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the requirements file into the container
COPY requirements.txt .

# Step 4: Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy your API code and your trained model weights into the container
COPY app.py .
COPY best_churn_model.pkl .
COPY numerical_scaler.pkl .
COPY numerical_cols_list.pkl .
COPY model_features_order.pkl .

# Step 6: Expose the port that FastAPI will run on
EXPOSE 8000

# Step 7: Run Uvicorn to start your FastAPI app when the container launches
# Note: We bind to host 0.0.0.0 so the cloud network can route internet traffic to it
CMD ["uvicorn", "app.py:app", "--host", "0.0.0.0", "--port", "8000"]