# Use a base image with Python
FROM python:3.11-slim

# Set up working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the application code
COPY . .

# Expose the port that Flask will run on
EXPOSE 8501

# Run the Flask app
CMD ["streamlit", "run", "app.py"]
