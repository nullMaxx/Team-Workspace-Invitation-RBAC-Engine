from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from app.api.v1.auth import router as auth_router
from app.api.v1.invitations import router as invitations_router
from app.api.v1.workspaces import router as workspaces_router
from app.core.config import settings
from app.core.database import engine
from app.models.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", docs_url="/docs", lifespan=lifespan)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(invitations_router, prefix="/api/v1")
app.include_router(workspaces_router, prefix="/api/v1")

@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}