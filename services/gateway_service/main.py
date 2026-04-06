from fastapi import FastAPI, Request
import httpx
from settings import AUTH_SERVICE_URL, JOB_SERVICE_URL, SKILL_ANALYZER_URL

app = FastAPI(title="HTTP Gateway Service")

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(request: Request, path: str):
    # Simple routing based on path prefix
    if path.startswith("auth/"):
        target_url = f"{AUTH_SERVICE_URL}/{path[5:]}"
    elif path.startswith("jobs/"):
        target_url = f"{JOB_SERVICE_URL}/{path[5:]}"
    elif path.startswith("skills/"):
        target_url = f"{SKILL_ANALYZER_URL}/{path[7:]}"
    else:
        # Default to auth or return 404
        return {"error": "Unknown service"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers={k: v for k, v in request.headers.items() if k.lower() not in ["host"]},
                params=request.query_params,
                content=await request.body()
            )
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}