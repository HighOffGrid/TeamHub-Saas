from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import memberships
from app.core.config import settings
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.organizations import router as organizations_router
from app.routes.projects import router as projects_router
from app.routes.tasks import router as tasks_router



app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-tenant SaaS API for team management",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1", tags=["Auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(organizations_router, prefix="/api/v1/organizations", tags=["Organizations"])
app.include_router(projects_router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(memberships.router, prefix="/api/v1", tags=["Memberships"])

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "version": settings.VERSION}