from fastapi import FastAPI

from .database import engine, Base
from . import models

from .routers import (
    auth_router,
    doctors,
    patients
)


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="Doctor Patient Management API",
    description="FastAPI backend for managing doctors and patients",
    version="1.0.0"
)


app.include_router(
    auth_router.router
)

app.include_router(
    doctors.router
)

app.include_router(
    patients.router
)


@app.get("/")
def root():

    return {
        "message": "Doctor Patient API is running"
    }