# Use the official Python image
FROM python:3.11

# Set environment variables for non-interactive install
ENV DEBIAN_FRONTEND=noninteractive

# Install essential packages for psycopg3 compatibility
RUN apt-get update && \
    apt-get install -y python3-dev build-essential libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . .

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for the application
EXPOSE 8080

# Run the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
