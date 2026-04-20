# Use slim Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy dependency file first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Default command (you can change this)
CMD ["bash", "run_pipeline.sh"]