# Step 1: Use an official Python runtime as a base image
FROM python:3.10-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy requirements first to leverage Docker caching layers
COPY requirements.txt .

# Step 4: Install all software dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy all project files into the container image
COPY . .

# Step 6: Expose the default Streamlit port
EXPOSE 8501

# Step 7: Run the application when the container starts
# Change the last line of your Dockerfile to this:
CMD ["python", "pipeline_orchestrator.py"]