import json
import re
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from app.models import AppItem, AppCreate, AppUpdate

DATA_FILE = Path(__file__).parent.parent / "data" / "apps.json"


def _slugify(text: str) -> str:
    """Generate a clean URL-friendly ID from a name."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-") or "app"


def get_all_apps() -> List[AppItem]:
    """Retrieve all apps from the JSON data file."""
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text("[]", encoding="utf-8")
        return []

    try:
        content = DATA_FILE.read_text(encoding="utf-8")
        raw_list = json.loads(content)
        return [AppItem(**item) for item in raw_list]
    except Exception:
        return []


def save_all_apps(apps: List[AppItem]) -> None:
    """Save the list of apps back to the JSON data file."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    serialized = [app.model_dump() for app in apps]
    DATA_FILE.write_text(json.dumps(serialized, indent=2), encoding="utf-8")


def get_app_by_id(app_id: str) -> Optional[AppItem]:
    """Find a specific app by ID."""
    apps = get_all_apps()
    for app in apps:
        if app.id == app_id:
            return app
    return None


def create_app(data: AppCreate) -> AppItem:
    """Add a new app to the registry."""
    apps = get_all_apps()
    
    # Generate unique ID
    base_id = _slugify(data.name)
    app_id = base_id
    counter = 1
    existing_ids = {a.id for a in apps}
    while app_id in existing_ids:
        app_id = f"{base_id}-{counter}"
        counter += 1

    new_app = AppItem(
        id=app_id,
        name=data.name,
        description=data.description,
        category=data.category or "General",
        url=data.url.strip(),
        icon=data.icon or "🚀",
        tags=data.tags or [],
        is_pinned=data.is_pinned,
        created_at=datetime.utcnow().isoformat() + "Z"
    )

    apps.append(new_app)
    save_all_apps(apps)
    return new_app


def update_app(app_id: str, updates: AppUpdate) -> Optional[AppItem]:
    """Update fields of an existing app."""
    apps = get_all_apps()
    for idx, app in enumerate(apps):
        if app.id == app_id:
            update_data = updates.model_dump(exclude_unset=True)
            updated_dict = app.model_dump()
            updated_dict.update(update_data)
            updated_app = AppItem(**updated_dict)
            apps[idx] = updated_app
            save_all_apps(apps)
            return updated_app
    return None


def delete_app(app_id: str) -> bool:
    """Delete an app by its ID."""
    apps = get_all_apps()
    new_apps = [a for a in apps if a.id != app_id]
    if len(new_apps) == len(apps):
        return False
    save_all_apps(new_apps)
    return True

