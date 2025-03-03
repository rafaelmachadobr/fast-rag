from fastapi import FastAPI

from src.api.fastapi import router

app = FastAPI()

app.include_router(router)
