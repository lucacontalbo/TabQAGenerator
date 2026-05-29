FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Gradino's pinned dependencies directly (independent of clone)
RUN curl -sSfL \
    https://raw.githubusercontent.com/softlab-unimore/Gradino/master/requirements.txt \
    | grep -v '^\s*#' | grep -v '^\s*$' > /tmp/gradino_req.txt \
    && pip install --no-cache-dir -r /tmp/gradino_req.txt

# Install transitive deps missing from Gradino's requirements.txt
RUN pip install --no-cache-dir rdflib

# Clone Gradino source from master (read-only — no modifications to this repo)
RUN git clone --depth 1 --branch master \
    https://github.com/softlab-unimore/Gradino.git /app/gradino

# Install backend dependencies
COPY backend/requirements.txt /app/backend_requirements.txt
RUN pip install --no-cache-dir -r /app/backend_requirements.txt

# Copy backend application
COPY backend/ /app/

# Create output directory
RUN mkdir -p /app/output

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
