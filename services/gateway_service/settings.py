import os

# Service URLs
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8000")
JOB_SERVICE_URL = os.getenv("JOB_SERVICE_URL", "http://job_service:8000")
SKILL_ANALYZER_URL = os.getenv("SKILL_ANALYZER_URL", "http://skill_analyzer:8000")

# Gateway settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))