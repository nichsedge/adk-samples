import os
from dataclasses import dataclass

DEFAULT_LOCATION = "us-central1"
DEFAULT_MODEL_ID = "gemini-2.0-pro"
DEFAULT_PORT = 8080


@dataclass(frozen=True)
class Settings:
    project_id: str
    location: str
    model_id: str
    google_api_key: str
    port: int

    @staticmethod
    def from_env() -> "Settings":
        project_id = os.getenv("PROJECT_ID", "").strip()
        google_api_key = os.getenv("GOOGLE_API_KEY", "").strip()
        location = os.getenv("LOCATION", DEFAULT_LOCATION).strip()
        model_id = os.getenv("MODEL_ID", DEFAULT_MODEL_ID).strip()
        port_str = os.getenv("PORT", str(DEFAULT_PORT)).strip()

        if not project_id:
            raise ValueError("PROJECT_ID environment variable is required")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")

        try:
            port = int(port_str)
        except ValueError as exc:
            raise ValueError(f"Invalid PORT value: {port_str}") from exc

        return Settings(
            project_id=project_id,
            location=location or DEFAULT_LOCATION,
            model_id=model_id or DEFAULT_MODEL_ID,
            google_api_key=google_api_key,
            port=port,
        )