# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Expose port 5000 for the Flask application
EXPOSE 5000

# Define the command to run the application using Gunicorn
# Using 'python -m gunicorn' explicitly ensures Gunicorn is run via the Python interpreter
# where it was installed, which can be more robust in some Docker environments.
# -w 4: Run with 4 worker processes (adjust based on CPU cores).
# -b 0.0.0.0:5000: Bind to all network interfaces on port 5000.
# app:app: Specifies the application entry point (the 'app' object in 'app.py').
CMD ["python", "-m", "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]