# Use official Python slim image for smaller footprint
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
# The auth_service package is copied as a sub-directory and uses package imports
# (e.g., "from auth_service.api.xxx import yyy") for this service.
COPY . /app/auth_service

# Expose the application port
EXPOSE 9000

# Run the application using uvicorn
# The module path auth_service.app:app matches the project's import structure
CMD ["uvicorn", "auth_service.app:app", "--host", "0.0.0.0", "--port", "9000"]
