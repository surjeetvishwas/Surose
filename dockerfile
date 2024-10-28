# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container
COPY . /app

# Copy the .env file into the container
# (Optional: you might want to use environment variables directly in production instead)
COPY .env /app/.env

# Expose the port Django will use
EXPOSE 8000

# Set environment variables for production
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=your_project_name.settings.production 

# Run migrations and collect static files
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Command to run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
