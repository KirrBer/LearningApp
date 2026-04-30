from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import models
import schemas
import auth
from db import engine
from db_methods import (
    create_user,
    get_existing_user,
    get_user_by_username,
    get_user_by_id,
    update_user_last_login,
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
async def verify_token(token: schemas.TokenResponse):
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


@app.get("/health")
def health():
    return {"status": "healthy"}
