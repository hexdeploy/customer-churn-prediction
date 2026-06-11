# Step 1: Use an official lightweight Python runtime
FROM python:3.11-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the requirements file into the container
COPY requirements.txt .

# Step 4: Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy everything into the working directory
COPY . .

# Step 6: Expose the port that FastAPI will run on
EXPOSE 8000

# Step 7: Explicitly tell Uvicorn to look at the module path inside /app
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]