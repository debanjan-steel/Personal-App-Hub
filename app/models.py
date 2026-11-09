from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class AppBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the application")
    description: str = Field(..., max_length=300, description="Brief description of the app")
    category: str = Field(default="General", max_length=50, description="App category (e.g. Finance, Productivity, AI)")
    url: str = Field(..., description="Target web URL where the app is hosted")
    icon: str = Field(default="🚀", max_length=10, description="Emoji or icon code representing the app")
    tags: List[str] = Field(default_factory=list, description="Keywords or search tags")
    is_pinned: bool = Field(default=False, description="Whether the app is pinned to the top")


class AppCreate(AppBase):
    pass


class AppUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    category: Optional[str] = Field(None, max_length=50)
    url: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=10)
    tags: Optional[List[str]] = None
    is_pinned: Optional[bool] = None


class AppItem(AppBase):
    id: str = Field(..., description="Unique slug or identifier")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class HealthCheckResult(BaseModel):
    app_id: str
    url: str
    status: str  # "online", "degraded", "offline"
    status_code: Optional[int] = None
    response_time_ms: Optional[int] = None
    error: Optional[str] = None
    checked_at: str

