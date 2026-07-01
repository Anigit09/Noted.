from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from notes_proj.routers.notes import router as general_router
from notes_proj.routers.user import router as user_router
from contextlib import asynccontextmanager
from notes_proj.database import database
@asynccontextmanager
async def lifespan(app:FastAPI):
    await database.connect()
    yield
    await database.disconnect()
app=FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_headers=["*"],
    allow_origins=["*"],
    allow_methods=["*"],
    allow_credentials=True
)
app.include_router(general_router)
app.include_router(user_router)
frontend_dir=Path(__file__).resolve().parent
app.mount("/",StaticFiles(directory=str(frontend_dir),html=True),name="frontend")


