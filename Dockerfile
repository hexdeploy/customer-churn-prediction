# Step 1: Use the full official Python 3.11 image (includes build tools for modern dependencies)
FROM python:3.11

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

# Step 7: Run Uvicorn using explicit module layout execution
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]