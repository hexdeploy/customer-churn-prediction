# Step 1: Use an official lightweight Python runtime
FROM python:3.11-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the requirements file into the container
COPY requirements.txt .

# Step 4: Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy EVERYTHING from your local folder into the container at once
# (This bypasses individual file tracking and casing bugs!)
COPY . .

# Step 6: Expose the port that FastAPI will run on
EXPOSE 8000

# Step 7: Run Uvicorn to start your FastAPI app when the container launches
CMD ["uvicorn", "app.py:app", "--host", "0.0.0.0", "--port", "8000"]