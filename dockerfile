# Use the official Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy requirements.txt first to leverage Docker caching
COPY requirements.txt ./



# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of your application code
COPY . .



# Specify the entry point for your application
ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000"]
