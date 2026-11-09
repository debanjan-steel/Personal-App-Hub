import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional
import httpx
from app.models import HealthCheckResult, AppItem

# Cache health results briefly (e.g. 60 seconds) to avoid slamming remote endpoints
_health_cache: Dict[str, HealthCheckResult] = {}
_cache_timestamp: float = 0
CACHE_TTL = 30.0  # seconds


async def check_single_app(app: AppItem, client: httpx.AsyncClient) -> HealthCheckResult:
    """Perform a ping to an app's public URL."""
    url = app.url
    start = time.perf_counter()
    try:
        # Try HEAD first for lightweight checking; fall back to GET if 405 Method Not Allowed
        response = await client.head(url, follow_redirects=True, timeout=5.0)
        if response.status_code == 405:
            response = await client.get(url, follow_redirects=True, timeout=5.0)

        elapsed_ms = int((time.perf_counter() - start) * 1000)

        # 2xx and 3xx indicate the app server is up and responding
        if 200 <= response.status_code < 400:
            status = "online"
        elif response.status_code in (401, 403):
            # Auth required, but the server is definitely running
            status = "online"
        else:
            status = "degraded"

        return HealthCheckResult(
            app_id=app.id,
            url=url,
            status=status,
            status_code=response.status_code,
            response_time_ms=elapsed_ms,
            checked_at=datetime.utcnow().isoformat() + "Z"
        )
    except httpx.TimeoutException:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return HealthCheckResult(
            app_id=app.id,
            url=url,
            status="offline",
            error="Connection timed out (5s)",
            response_time_ms=elapsed_ms,
            checked_at=datetime.utcnow().isoformat() + "Z"
        )
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return HealthCheckResult(
            app_id=app.id,
            url=url,
            status="offline",
            error=str(exc) or "Unreachable",
            response_time_ms=elapsed_ms,
            checked_at=datetime.utcnow().isoformat() + "Z"
        )


async def check_all_apps(apps: List[AppItem], force_refresh: bool = False) -> List[HealthCheckResult]:
    """Check status of all registered apps concurrently."""
    global _health_cache, _cache_timestamp
    now = time.time()

    if not force_refresh and (now - _cache_timestamp) < CACHE_TTL and _health_cache:
        # Return cached results if valid
        return [_health_cache[a.id] for a in apps if a.id in _health_cache]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppHub-HealthCheck/1.0"
    }

    async with httpx.AsyncClient(headers=headers, verify=False) as client:
        tasks = [check_single_app(app, client) for app in apps]
        results = await asyncio.gather(*tasks)

    # Update cache
    _health_cache = {r.app_id: r for r in results}
    _cache_timestamp = now
    return results

