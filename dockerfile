# Use the official Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy requirements.txt and .env file
COPY requirements.txt ./
COPY .env ./


# Install Python dependencies
RUN pip install -r requirements.txt --verbose

# Copy the rest of your application code
COPY . .



# Command to run the application using Django's development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
