# Cloud Run-friendly image for FastAPI + ADK
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps (if any heavy libs needed later, add here)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project metadata first to leverage Docker layer caching
COPY research_agent_adk/pyproject.toml ./pyproject.toml

# Install with pip (uv is used locally; inside container we can still leverage pip)
# Using --no-cache-dir is redundant with PIP_NO_CACHE_DIR but kept explicit
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
 && pip install --no-cache-dir .

# Copy the rest of the source
COPY research_agent_adk/README.md ./README.md
COPY research_agent_adk/research_agent_adk ./research_agent_adk
COPY research_agent_adk/start.sh ./start.sh

# Make start script executable
RUN chmod +x ./start.sh

# Cloud Run sets PORT env; default to 8080 for local runs
ENV PORT=8080
EXPOSE 8080

# Runtime environment variables expected:
# - GOOGLE_API_KEY (required)
# - PROJECT_ID (required)
# - LOCATION (optional, default us-central1)
# - MODEL_ID (optional, default gemini-2.0-pro)

# Start FastAPI via uvicorn
CMD ["./start.sh"]