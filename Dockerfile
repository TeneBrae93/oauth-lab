# Use an official, lightweight Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code (app.py, static/, templates/)
COPY . .

# Expose port 80 to the outside world
EXPOSE 80

# Run the Flask application
# The base image runs as root by default, allowing it to bind to port 80
CMD ["python", "app.py"]