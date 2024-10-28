# Use the official Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy requirements.txt and .env file
COPY requirements.txt ./
COPY .env ./

# Update package list and install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies
RUN pip install -r requirements.txt 
RUN sudo apt-get install python3-dev default-libmysqlclient-dev build-essential

# Copy the rest of your application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "app.py"]
