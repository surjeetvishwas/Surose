# Use the official Python image
FROM python:3.10

# Set environment variables for non-interactive install
ENV DEBIAN_FRONTEND=noninteractive

# Install required system packages for mysqlclient
RUN apt-get update && \
    apt-get install -y python3-dev default-libmysqlclient-dev build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install Python dependencies
RUN pip install asgiref==3.7.2 certifi==2023.11.17 charset-normalizer==3.3.2 Django==5.0 \
    django-cleanup==8.0.0 djangorestframework==3.14.0 idna==3.6 mysqlclient==2.2.5 \
    Pillow==10.1.0 python-dotenv==1.0.0 pytz==2023.3.post1 requests==2.32.3 sqlparse==0.4.4 \
    stripe==8.8.0 typing_extensions==4.9.0 tzdata==2023.3 urllib3==2.1.0

# Copy the application code
COPY . .

# Expose port 8080 for Google Cloud Run
EXPOSE 8080

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
