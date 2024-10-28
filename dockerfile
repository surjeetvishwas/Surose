# Use the official Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy requirements.txt and .env file
COPY requirements.txt ./
COPY .env ./

# Update pip and install build essentials
RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install -r requirements.txt --verbose

# Copy the rest of your application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "app.py"]
