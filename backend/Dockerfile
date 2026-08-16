# Use a minimal base image with Python 3.9 installed
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the current directory to the container's working directory
COPY . .

# Install dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 7860 for the Flask API
EXPOSE 7860

# Start the application using Gunicorn with 4 worker processes on port 7860
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:app"]
