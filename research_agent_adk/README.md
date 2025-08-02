# Research Agent ADK (FastAPI + Cloud Run)

An ADK-based research agent focused on "Agentic AI for Enterprise". It uses Gemini 2.0 Pro with the ADK `Agent` and the built-in `google_search` tool to research, synthesize, and return sourced answers via a simple HTTP API suitable for Cloud Run.

## Features
- FastAPI service with:
  - GET /health for health checks
  - POST /query to ask research questions and receive synthesized answers plus sources
- ADK Agent configured with tools:
  - google_search for web research
  - summarize_sources to generate a concise enterprise-focused synthesis
- Configurable via environment variables:
  - GOOGLE_API_KEY
  - PROJECT_ID
  - LOCATION (default: us-central1)
  - MODEL_ID (default: gemini-2.0-pro)

## Quickstart (Local)
1) Create a virtual env or use uv:
   - uv pip install -e .
2) Set env:
   - export GOOGLE_API_KEY=<your-gemini-api-key>
   - export PROJECT_ID=<your-gcp-project-id>
   - export LOCATION=us-central1
   - export MODEL_ID=gemini-2.0-pro
3) Run:
   - ./start.sh
   or
   - uvicorn research_agent_adk.server:app --host 0.0.0.0 --port 8080

POST example:
```
curl -s http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Summarize agentic AI adoption patterns for large enterprises and cite 3 credible sources."}'
```

## Cloud Run Deployment (Summary)
- Build image: docker build -t gcr.io/$PROJECT_ID/research-agent-adk:latest -f Dockerfile .
- Push: gcloud auth configure-docker && docker push gcr.io/$PROJECT_ID/research-agent-adk:latest
- Deploy:
```
gcloud run deploy research-agent-adk \
  --image gcr.io/$PROJECT_ID/research-agent-adk:latest \
  --region $LOCATION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars PROJECT_ID=$PROJECT_ID,LOCATION=$LOCATION,MODEL_ID=gemini-2.0-pro \
  --set-secrets GOOGLE_API_KEY=GOOGLE_API_KEY:latest
```
See the repository-level guide for a more detailed GCP setup, including service account IAM and Workload Identity.

## Notes
- Ensure ADK and Google SDK versions are compatible.
- The SSE streaming endpoint is planned as a future enhancement.