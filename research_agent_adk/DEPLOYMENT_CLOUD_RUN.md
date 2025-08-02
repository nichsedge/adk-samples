# Deploy Research Agent ADK to Google Cloud Run

This guide walks through building and deploying the FastAPI-based ADK Research Agent to Cloud Run. The service exposes:
- GET /health
- POST /query with JSON: {"question": "...", "max_sources": 5}

It uses Gemini 2.0 Pro via ADK and the built-in google_search tool. Configure environment with PROJECT_ID, LOCATION, MODEL_ID, and GOOGLE_API_KEY.

## Prerequisites

1) GCP project and billing enabled
2) gcloud CLI installed and authenticated
3) Docker installed and authenticated to push images to Artifact Registry or Container Registry
4) Permissions: You need roles to build and deploy (Project Editor is easiest for initial setup)

Authenticate:
```
gcloud auth login
gcloud config set project $PROJECT_ID
gcloud auth configure-docker
```

Optionally set common env:
```
export PROJECT_ID="your-project-id"
export LOCATION="us-central1"
export IMAGE_NAME="research-agent-adk"
export IMAGE="gcr.io/${PROJECT_ID}/${IMAGE_NAME}:latest"
```

## Enable APIs

Cloud Run and Secret Manager are typically required, plus Vertex AI if you plan to use Agent Engine later:
```
gcloud services enable run.googleapis.com secretmanager.googleapis.com aiplatform.googleapis.com
```

## Create Secret for GOOGLE_API_KEY

Store your Gemini API key in Secret Manager:
```
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create GOOGLE_API_KEY --replication-policy="automatic" --data-file=-
# Or update an existing secret:
# echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets versions add GOOGLE_API_KEY --data-file=-
```

Grant the Cloud Run service account permission to access this secret after you deploy (or pre-create a service account and grant access now; see IAM below).

## Build and Push Container

From repo root:
```
docker build -t "$IMAGE" -f research_agent_adk/Dockerfile .
docker push "$IMAGE"
```

## Create or Choose Service Account (Recommended)

Create a least-privileged service account for the service:
```
gcloud iam service-accounts create adk-research-sa \
  --display-name "ADK Research Agent SA"
```

Grant minimum roles:
- For basic Cloud Run execution and logging:
```
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:adk-research-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role "roles/run.invoker"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:adk-research-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role "roles/logging.logWriter"
```

- To read secret value:
```
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member "serviceAccount:adk-research-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role "roles/secretmanager.secretAccessor"
```

(If you later deploy to Vertex AI Agent Engine, you may need additional roles; not required for this basic HTTP service.)

## Deploy to Cloud Run

Deploy with environment variables and Secret reference:
```
gcloud run deploy research-agent-adk \
  --image "$IMAGE" \
  --region "$LOCATION" \
  --platform managed \
  --service-account "adk-research-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --allow-unauthenticated \
  --set-env-vars "PROJECT_ID=${PROJECT_ID},LOCATION=${LOCATION},MODEL_ID=gemini-2.0-pro" \
  --set-secrets "GOOGLE_API_KEY=GOOGLE_API_KEY:latest"
```

Notes:
- The container listens on PORT=8080 (Cloud Run default).
- You can restrict access by removing --allow-unauthenticated and granting run.invoker to specific identities only.

## Test the Deployment

Get the service URL:
```
SERVICE_URL=$(gcloud run services describe research-agent-adk --region "$LOCATION" --format 'value(status.url)')
echo "$SERVICE_URL"
```

Health check:
```
curl -s "$SERVICE_URL/health"
```

Query example:
```
curl -s "$SERVICE_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"question":"Summarize enterprise adoption patterns of agentic AI and cite 3 credible sources.","max_sources":5}'
```

Expected response schema:
```
{
  "answer": "... synthesized answer ...",
  "sources": [ { "title": "...", "url": "...", "snippet": "..." }, ... ]
}
```

## Local Development

Install dependencies (using uv or pip):
```
cd research_agent_adk
uv pip install -e .
# or: pip install -e .
```

Export env and run:
```
export GOOGLE_API_KEY="your-key"
export PROJECT_ID="your-project"
export LOCATION="us-central1"
export MODEL_ID="gemini-2.0-pro"
./start.sh
# Visit http://localhost:8080/health
```

Run tests:
```
pytest -q
```

## Production Considerations

- Authentication & Secrets
  - Store GOOGLE_API_KEY in Secret Manager and mount via --set-secrets (as above).
  - Avoid embedding secrets in images.
- Quotas and costs
  - Monitor usage in Cloud Monitoring and set budgets/alerts.
- Observability
  - Add structured logs around tool calls and responses (Runner events).
- Hardening
  - Remove --allow-unauthenticated for private services; front with IAP or Cloud Endpoints if required.
- Scalability
  - Tune concurrency (default 80) and min/max instances per workload needs:
```
gcloud run services update research-agent-adk \
  --region "$LOCATION" \
  --concurrency 10 \
  --min-instances 0 \
  --max-instances 5
```

## Roadmap: SSE Streaming Endpoint

Planned GET /stream?question=... to stream partial tokens and tool events:
- Use FastAPI StreamingResponse
- Hook into Runner.run_live() (see ADK docs snippets) to yield incremental content
- Gate via flag ENABLE_SSE=true

This is left for a future iteration to keep the current deployment simple and robust.