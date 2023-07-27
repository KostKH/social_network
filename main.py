from fastapi import FastAPI

from config import settings
from entrypoints.main_router import main_router

app = FastAPI(title=settings.app_title)
app.include_router(main_router)
