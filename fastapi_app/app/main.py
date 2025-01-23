from fastapi import FastAPI
from app.routers import branches

app = FastAPI(
    title="GitHub API Proxy - Repository Branch Management",
    description="Proxy API for managing GitHub repository branches via Git Data API.",
    version="1.0.0",
    contact={
        "name": "Support",
        "email": "support@pm.fountain.coach"
    },
    servers=[
        {"url": "https://branches.pm.fountain.coach", "description": "Proxy server for GitHub repository branches."}
    ],
)

app.include_router(branches.router)
                