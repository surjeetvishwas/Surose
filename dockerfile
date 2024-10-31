# Use the official Python image
FROM python:3.11

# Set environment variables for non-interactive install
ENV DEBIAN_FRONTEND=noninteractive

# Install essential packages for psycopg2 compatibility
RUN apt-get update && apt-get install -y libpq-dev python3-dev

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . .

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set Django settings for production
ENV DJANGO_SETTINGS_MODULE=project.settings

# Collect static files
RUN mkdir -p /app/static && chmod 755 /app/static
RUN python manage.py collectstatic --noinput

# Expose port for the application
EXPOSE 8080

# Run the Django application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "project.wsgi:application"]
