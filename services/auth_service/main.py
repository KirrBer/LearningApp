from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import schemas
import auth
from auth_service.db import engine
from auth_service.db_methods import (
    create_user,
    get_existing_user,
    get_user_by_username,
    get_user_by_id,
    get_user_skills,
    update_user_last_login,
    update_user_profile,
    update_user_resume,
    update_user_skills,
)



app = FastAPI(title="Auth Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/register", response_model=schemas.UserResponse)
async def register(user: schemas.UserCreate):
    existing_user = await get_existing_user(user.email, user.username)

    if existing_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")

    hashed_password = auth.get_password_hash(user.password)
    db_user = await create_user(
        email=user.email,
        username=user.username,
        password_hash=hashed_password,
        full_name=user.full_name,
    )

    return db_user


@app.post("/login", response_model=schemas.TokenResponse)
async def login(user: schemas.UserLogin):
    db_user = await get_user_by_username(user.username)

    if not db_user or not auth.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not db_user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive")

    db_user = await update_user_last_login(str(db_user.id))

    access_token = auth.create_access_token(data={"sub": str(db_user.id)})
    refresh_token = auth.create_refresh_token(data={"sub": str(db_user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@app.post("/verify", response_model=schemas.TokenValidationResponse)
async def verify_token(token: schemas.TokenVerify):
    payload = auth.verify_access_token(token.access_token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    db_user = await get_user_by_id(user_id)

    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")

    if not db_user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive")

    return {
        "valid": True,
        "user_id": user_id,
        "message": "Token is valid",
    }


@app.post("/refresh", response_model=schemas.TokenRefreshResponse)
async def refresh_access_token(token_data: schemas.TokenRefresh):
    payload = auth.verify_refresh_token(token_data.refresh_token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user_id = payload.get("sub")
    db_user = await get_user_by_id(user_id)

    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")

    if not db_user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive")

    new_access_token = auth.create_access_token(data={"sub": str(db_user.id)})

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }


async def get_current_user_id(request: Request) -> str:
    authorization = request.headers.get("Authorization", "")
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ", 1)[1]
    payload = auth.verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token does not contain user id")

    return user_id


@app.get("/profile", response_model=schemas.UserProfileResponse)
async def get_profile(request: Request):
    user_id = await get_current_user_id(request)
    db_user = await get_user_by_id(user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user


@app.put("/profile", response_model=schemas.UserProfileResponse)
async def update_profile(request: Request, payload: schemas.ProfileUpdateRequest):
    user_id = await get_current_user_id(request)
    db_user, error = await update_user_profile(
        user_id,
        str(payload.email),
        payload.username,
        payload.full_name,
    )

    if error == "Email is already registered":
        raise HTTPException(status_code=409, detail=error)
    if error == "Username is already registered":
        raise HTTPException(status_code=409, detail=error)
    if error == "Username must contain at least 3 characters":
        raise HTTPException(status_code=422, detail=error)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user


@app.put("/profile/resume", response_model=schemas.UserProfileResponse)
async def save_profile_resume(request: Request, payload: schemas.ResumeUpdateRequest):
    user_id = await get_current_user_id(request)
    db_user = await update_user_resume(user_id, payload.resume)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user


@app.get("/profile/skills", response_model=schemas.UserSkillsResponse)
async def get_profile_skills(request: Request):
    user_id = await get_current_user_id(request)
    skills = await get_user_skills(user_id)
    return {"skills": skills}


@app.put("/profile/skills", response_model=schemas.UserSkillsResponse)
async def save_profile_skills(request: Request, payload: schemas.SkillsUpdateRequest):
    user_id = await get_current_user_id(request)
    skills = await update_user_skills(user_id, payload.skills)
    return {"skills": skills}


@app.get("/health")
def health():
    return {"status": "healthy"}
