from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import create_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all()
    yield


app = FastAPI(
    title="Hooli Heard",
    description="Voice of Customer intelligence platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
from app.api.insights import router as insights_router  # noqa: E402
from app.api.dashboard import router as dashboard_router  # noqa: E402
from app.api.accounts import router as accounts_router  # noqa: E402

app.include_router(insights_router)
app.include_router(dashboard_router)
app.include_router(accounts_router)


@app.get("/")
def root():
    return {"status": "ok", "project": "Hooli Heard"}
