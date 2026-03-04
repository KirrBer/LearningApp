from fastapi import FastAPI
from routes import router
from model_manager import model_manager
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    model_manager.load_models()
    yield
    model_manager.unload_models()
 
app = FastAPI(lifespan=lifespan)
app.include_router(router)