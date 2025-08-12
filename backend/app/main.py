from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import policies as policies_router, portfolio as portfolio_router, quotes as quotes_router
from .core.middleware import RateLimitMiddleware
from .core.settings import settings

# Alembic is used for migrations, do not call Base.metadata.create_all here in production
app = FastAPI(title="Insurance Advisor V6", root_path=settings.BASE_PATH)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(policies_router.router)
app.include_router(portfolio_router.router)
app.include_router(quotes_router.router)