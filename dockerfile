# Use the official Python image
FROM python:3.11

# Set environment variables for non-interactive install
ENV DEBIAN_FRONTEND=noninteractive

# Install required system packages for PostgreSQL client
RUN apt-get update && \
    apt-get install -y python3-dev libpq-dev build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir \
    asgiref==3.7.2 certifi==2023.11.17 charset-normalizer==3.3.2 Django==5.0 \
    django-cleanup==8.0.0 djangorestframework==3.14.0 idna==3.6 psycopg2-binary==2.9.7 \
    Pillow==10.1.0 python-dotenv==1.0.0 pytz==2023.3.post1 requests==2.32.3 sqlparse==0.4.4 \
    stripe==8.8.0 typing_extensions==4.9.0 tzdata==2023.3 urllib3==2.1.0

# Expose port 8080 for the application
EXPOSE 8080

# Set the entrypoint to use the Python command directly
ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8080"]
