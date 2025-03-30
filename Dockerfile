# Use official Python image
FROM python:3.10

# Set working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

COPY .env .env

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set environment variable for Tesseract path
ENV TESSERACT_CMD=/usr/bin/tesseract

# Expose port (FastAPI default is 8000)
EXPOSE 8000

# Start the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
