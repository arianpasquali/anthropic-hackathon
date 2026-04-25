from fastapi import FastAPI

from src.backend.database import create_db_and_tables

app = FastAPI(title="Klimaatkracht")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Routers registered below as they are implemented
from src.backend.routers import auth as auth_router  # noqa: E402
app.include_router(auth_router.router)
