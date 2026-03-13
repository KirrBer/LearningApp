from fastapi import FastAPI
from skill_analyzer.routes import router
from skill_analyzer.model_manager import model_manager
from skill_analyzer.kafka import kafka_manager
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    model_manager.load_models()
    await kafka_manager.start()
    yield
    model_manager.unload_models()
 
app = FastAPI(lifespan=lifespan)
app.include_router(router)