from fastapi import FastAPI
from app.api.routers.health import router as health_router
from app.api.routers.health_db import router as health_db_router
from app.api.routers.auth import router as auth_router
from app.api.routers.invites import router as invites_router
from app.api.routers.properties import router as properties_router
from app.api.routers.units import router as units_router
from app.api.routers.user_units import router as user_units_router

app = FastAPI(title="Hausportal API")

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(health_db_router, prefix="/health", tags=["health"])

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(invites_router, prefix="/invites", tags=["invites"])

app.include_router(properties_router, prefix="/properties", tags=["properties"])
app.include_router(units_router, prefix="/units", tags=["units"])
app.include_router(user_units_router, prefix="/user-units", tags=["user_units"])
