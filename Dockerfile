FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone Gradino (read-only — no modifications to this repo)
RUN git clone --depth 1 https://github.com/softlab-unimore/Gradino.git /app/gradino

# Install Gradino's dependencies
RUN pip install --no-cache-dir -r /app/gradino/requirements.txt

# Install backend dependencies
COPY backend/requirements.txt /app/backend_requirements.txt
RUN pip install --no-cache-dir -r /app/backend_requirements.txt

# Copy backend application
COPY backend/ /app/

# Create output directory
RUN mkdir -p /app/output

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
