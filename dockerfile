# Use the official Python image
FROM python:3.11

# Set environment variables for non-interactive install
ENV DEBIAN_FRONTEND=noninteractive

# Install required system packages for PostgreSQL (psycopg2 dependency) and other dependencies
RUN apt-get update && \
    apt-get install -y python3-dev libpq-dev build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the application code and requirements file
COPY . .
COPY requirements.txt .

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 8000

# Set the entrypoint to use the Python command directly
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
