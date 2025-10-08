# Use an official Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy dependency file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project files
COPY . .

# Expose the port Flask runs on
EXPOSE 8000

# Define the default command to run your app
CMD ["python", "app.py"]
