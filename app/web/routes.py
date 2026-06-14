"""Serve the PWA shell: index, manifest, service worker, icons.

These routes are public (no access code) so the shell can load; the JS then
authenticates against /api via the access code. Static assets are cached by
the service worker for an app-like, offline-tolerant launch.
"""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, Response

STATIC_DIR = Path(__file__).parent / "static"

router = APIRouter(tags=["web"])


@router.get("/", include_in_schema=False)
@router.get("/login", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


@router.get("/manifest.webmanifest", include_in_schema=False)
def manifest():
    return FileResponse(STATIC_DIR / "manifest.webmanifest",
                        media_type="application/manifest+json")


@router.get("/sw.js", include_in_schema=False)
def service_worker():
    # Served from root so its scope controls the whole app.
    return FileResponse(STATIC_DIR / "sw.js", media_type="application/javascript",
                        headers={"Cache-Control": "no-cache"})
