from fastapi import FastAPI

from src.backend.database import create_db_and_tables

app = FastAPI(title="Klimaatkracht")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Routers registered below as they are implemented
from src.backend.routers import auth as auth_router  # noqa: E402
from src.backend.routers import marketplace as marketplace_router  # noqa: E402
from src.backend.routers import checkout as checkout_router  # noqa: E402
from src.backend.routers import dashboard as dashboard_router  # noqa: E402
from src.backend.routers import admin as admin_router  # noqa: E402
app.include_router(auth_router.router)
app.include_router(marketplace_router.router)
app.include_router(checkout_router.router)
app.include_router(dashboard_router.router)
app.include_router(admin_router.router)
