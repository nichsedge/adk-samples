#!/usr/bin/env bash
set -euo pipefail

: "${PORT:=8080}"

exec uvicorn research_agent_adk.server:app --host 0.0.0.0 --port "${PORT}"