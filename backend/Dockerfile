FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files (except what's in .dockerignore)
COPY . .

# Expose Django's default port
EXPOSE 8000

# Default command to run Django server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
