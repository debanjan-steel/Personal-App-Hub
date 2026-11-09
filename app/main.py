import socket
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, APIRouter, HTTPException, Query, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.models import AppItem, AppCreate, AppUpdate, HealthCheckResult
from app.storage import (
    get_all_apps,
    get_app_by_id,
    create_app,
    update_app,
    delete_app
)
from app.health import check_all_apps

app = FastAPI(
    title="Universal Personal App Hub",
    description="A centralized, mobile-first launchpad and health monitor for your self-built projects.",
    version="1.0.0",
    redirect_slashes=False
)

# Enable CORS for cross-device & mobile client access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
PUBLIC_DIR = BASE_DIR / "public"


def get_local_ip() -> str:
    """Best-effort discovery of local LAN IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


# API Router - Works with or without /api prefix
router = APIRouter()


@router.get("/info")
def get_hub_info():
    """Returns metadata about the hub and connectivity."""
    return {
        "title": "Universal Personal App Hub",
        "version": "1.0.0",
        "local_ip": get_local_ip(),
        "default_port": 8000,
        "is_online_ready": True
    }


@router.get("/apps", response_model=List[AppItem])
def list_apps(
    search: Optional[str] = Query(None, description="Search term for name, description or tags"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    apps = get_all_apps()
    
    if category and category.lower() != "all":
        apps = [a for a in apps if a.category.lower() == category.lower()]

    if search:
        s = search.lower()
        apps = [
            a for a in apps
            if s in a.name.lower() or s in a.description.lower() or any(s in tag.lower() for tag in a.tags)
        ]

    # Sort: pinned apps first, then alphabetically
    return sorted(apps, key=lambda a: (not a.is_pinned, a.name.lower()))


@router.get("/categories")
def list_categories():
    apps = get_all_apps()
    cats = {}
    for a in apps:
        cat = a.category or "General"
        cats[cat] = cats.get(cat, 0) + 1
    return [{"name": name, "count": count} for name, count in sorted(cats.items())]


@router.post("/apps", response_model=AppItem, status_code=status.HTTP_201_CREATED)
def add_app(data: AppCreate):
    return create_app(data)


@router.get("/apps/{app_id}", response_model=AppItem)
def get_single_app(app_id: str):
    app = get_app_by_id(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    return app


@router.put("/apps/{app_id}", response_model=AppItem)
def edit_app(app_id: str, data: AppUpdate):
    updated = update_app(app_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="App not found")
    return updated


@router.delete("/apps/{app_id}")
def remove_app(app_id: str):
    success = delete_app(app_id)
    if not success:
        raise HTTPException(status_code=404, detail="App not found")
    return {"message": "App deleted successfully", "id": app_id}


@router.get("/health", response_model=List[HealthCheckResult])
async def health_check_all(force: bool = False):
    apps = get_all_apps()
    return await check_all_apps(apps, force_refresh=force)


# Mount router at BOTH /api and / to prevent any prefix mismatch on serverless platforms
app.include_router(router, prefix="/api")
app.include_router(router)


# Static and PWA file handlers
@app.get("/manifest.json", include_in_schema=False)
def get_manifest():
    for d in [PUBLIC_DIR, STATIC_DIR]:
        f = d / "manifest.json"
        if f.exists():
            return FileResponse(f, media_type="application/manifest+json")
    raise HTTPException(status_code=404, detail="manifest.json not found")


@app.get("/sw.js", include_in_schema=False)
def get_service_worker():
    for d in [PUBLIC_DIR, STATIC_DIR]:
        f = d / "sw.js"
        if f.exists():
            return FileResponse(f, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="sw.js not found")


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

if PUBLIC_DIR.exists():
    app.mount("/public", StaticFiles(directory=str(PUBLIC_DIR)), name="public")


@app.get("/")
def serve_dashboard():
    for d in [PUBLIC_DIR, STATIC_DIR]:
        index_file = d / "index.html"
        if index_file.exists():
            return FileResponse(index_file, media_type="text/html")
    return {"message": "Universal Personal App Hub API is running."}


@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all_debug(request: Request, path_name: str):
    return {
        "debug": True,
        "scope_path": request.scope.get("path"),
        "url_path": request.url.path,
        "path_name": path_name
    }

