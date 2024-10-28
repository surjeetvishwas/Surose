# Use the official Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy requirements.txt first to leverage Docker caching
COPY requirements.txt ./

# Install system dependencies for mysqlclient and others
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install -r requirements.txt --verbose

# Copy the rest of your application code
COPY . .

# Expose the port your app runs on (change if needed)
EXPOSE 8000

# Command to run the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
