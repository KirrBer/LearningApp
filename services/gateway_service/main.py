from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import httpx
from settings import AUTH_SERVICE_URL, JOB_SERVICE_URL, SKILL_ANALYZER_URL

app = FastAPI(title="HTTP Gateway Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UNPROTECTED_PATHS = {
    "auth/login",
    "auth/register",
    "auth/refresh",
    "auth/verify",
    "api/auth/login",
    "api/auth/register",
    "api/auth/refresh",
    "api/auth/verify",
    "health",
    "api/health",
}


def build_target_url(path: str) -> str | None:
    if path.startswith("api/auth/"):
        return f"{AUTH_SERVICE_URL}/{path[len('api/auth/'):]}"
    if path.startswith("auth/"):
        return f"{AUTH_SERVICE_URL}/{path[len('auth/'):]}"
    if path.startswith("api/job_service/"):
        return f"{JOB_SERVICE_URL}/{path[len('api/job_service/'):]}"
    if path.startswith("job_service/"):
        return f"{JOB_SERVICE_URL}/{path[len('job_service/'):]}"
    if path.startswith("api/skill_analyzer/"):
        return f"{SKILL_ANALYZER_URL}/{path[len('api/skill_analyzer/'):]}"
    if path.startswith("skill_analyzer/"):
        return f"{SKILL_ANALYZER_URL}/{path[len('skill_analyzer/'):]}"
    return None


def needs_authorization(path: str) -> bool:
    if path in UNPROTECTED_PATHS:
        return False
    if path.startswith("api/auth/") or path.startswith("auth/"):
        return True
    if path.startswith("api/job_service/") or path.startswith("jobs/"):
        return True
    if path.startswith("api/skill_analyzer/") or path.startswith("skills/"):
        return True
    return False


async def verify_access_token(token: str) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTH_SERVICE_URL}/verify",
            json={"access_token": token},
            timeout=10.0,
        )
        return response.status_code == 200


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path.lstrip("/")
    if needs_authorization(path):
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.lower().startswith("bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid Authorization header"},
            )

        access_token = authorization.split(" ", 1)[1]
        try:
            if not await verify_access_token(access_token):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid or expired token"},
                )
        except httpx.RequestError:
            return JSONResponse(
                status_code=503,
                content={"detail": "Authentication service unavailable"},
            )

    return await call_next(request)


@app.get("/api/health")
async def health():
    statuses = {
        "gateway": "healthy",
    }
    async with httpx.AsyncClient() as client:
        services = {
            "auth": AUTH_SERVICE_URL,
            "job_service": JOB_SERVICE_URL,
            "skill_analyzer": SKILL_ANALYZER_URL,
        }
        for name, url in services.items():
            try:
                response = await client.get(f"{url}/health", timeout=5.0)
                statuses[name] = "healthy" if response.status_code == 200 else f"unhealthy ({response.status_code})"
            except httpx.HTTPError as exc:
                statuses[name] = f"unavailable ({str(exc)})"
    return statuses


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy_request(request: Request, path: str):
    target_url = build_target_url(path)
    if not target_url:
        return JSONResponse(status_code=404, content={"detail": "Unknown service route"})

    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in {"host", "content-length"}
    }
    body = await request.body()

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=request.query_params,
            content=body,
            timeout=30.0,
        )

    response_headers = {
        key: value
        for key, value in response.headers.items()
        if key.lower() not in {"content-encoding", "transfer-encoding", "content-length", "connection"}
    }

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=response_headers,
        media_type=response.headers.get("content-type"),
    )
