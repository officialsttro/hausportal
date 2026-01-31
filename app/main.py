from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.health import router as health_router
from app.api.routers.health_db import router as health_db_router
from app.api.routers.auth import router as auth_router
from app.api.routers.invites import router as invites_router
from app.api.routers.properties import router as properties_router
from app.api.routers.units import router as units_router
from app.api.routers.user_units import router as user_units_router
from app.api.routers.tickets import router as tickets_router
from app.api.routers.documents import router as documents_router

app = FastAPI(title="Hausportal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.2.202:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(health_db_router)
app.include_router(auth_router)
app.include_router(invites_router)
app.include_router(properties_router)
app.include_router(units_router)
app.include_router(user_units_router)
app.include_router(tickets_router)
app.include_router(documents_router)
