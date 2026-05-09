from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
from db import Base, engine, get_db

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    # Just log the error and continue — don't crash on import
    print(f"[WARNING] Could not connect to database: {e}")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
