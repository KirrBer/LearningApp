from fastapi import FastAPI
from .routes import router
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.include_router(router)