from contextlib import asynccontextmanager
from tkinter import EXCEPTION
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from db import Base, engine, get_db
import logging


logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        # Startup
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
        
        # Shutdown 
        await engine.dispose()
    except Exception as e:
        logger.error(f"Could not connect to database: {e}")

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")
templates = Jinja2Templates(directory="templates")
