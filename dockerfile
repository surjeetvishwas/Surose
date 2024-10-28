# Use the official Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Install system dependencies for mysqlclient
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first to leverage Docker caching
COPY requirements.txt ./

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port your app runs on (change if needed)
EXPOSE 8000

# Specify the entry point for your application
ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000"]
