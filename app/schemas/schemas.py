from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.core.wordlists import SUPPORTED_LANGUAGES
from app.models.models import CodenameStatus, GenerationStyle

# ── Generate ──────────────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    count: int = Field(1, ge=1, le=50)
    style: GenerationStyle = GenerationStyle.MILITARY
    language: str = Field("en", description="ISO 639-1 code")
    word_count: int = Field(2, ge=1, le=4)
    separator: str = Field("space", description="space | dash | underscore | dot")
    namespace: str = Field("global")
    assign_to: Optional[str] = Field(None, description="Entity to assign to, e.g. 'user:99'")
    meta: dict = {}

    @field_validator("language")
    @classmethod
    def check_language(cls, v):
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Language must be one of {SUPPORTED_LANGUAGES}")
        return v

    @field_validator("separator")
    @classmethod
    def check_separator(cls, v):
        allowed = {"space", "dash", "underscore", "dot"}
        if v not in allowed:
            raise ValueError(f"Separator must be one of {allowed}")
        return v


class GenerateResponse(BaseModel):
    codenames: List[str]
    style: str
    language: str
    namespace: str
    generated_count: int
    ids: List[int]


# ── Namespace ─────────────────────────────────────────────────────────────────

class NamespaceCreate(BaseModel):
    slug: str = Field(..., min_length=2, max_length=80, pattern=r"^[a-z0-9\-_]+$")
    description: Optional[str] = None
    owner: Optional[str] = None


class NamespaceOut(BaseModel):
    id: int
    slug: str
    description: Optional[str]
    owner: Optional[str]
    created_at: datetime
    is_active: bool
    codename_count: int = 0

    model_config = {"from_attributes": True}


class SaturationReport(BaseModel):
    namespace: str
    style: str
    language: str
    word_count: int
    pool_size: int
    active_count: int
    saturation_pct: float
    estimated_remaining: int


# ── Codename ──────────────────────────────────────────────────────────────────

class CodenameOut(BaseModel):
    id: int
    value: str
    style: GenerationStyle
    language: str
    word_count: int
    separator: str
    status: CodenameStatus
    namespace_id: int
    assigned_to: Optional[str]
    assigned_at: Optional[datetime]
    retired_at: Optional[datetime]
    use_count: int
    generated_at: datetime
    eligible_recycle_at: Optional[datetime]
    meta: dict

    model_config = {"from_attributes": True}


class RetireRequest(BaseModel):
    reason: Optional[str] = None


# ── Stats ─────────────────────────────────────────────────────────────────────

class StyleStats(BaseModel):
    style: str
    total_generated: int
    active: int
    retired: int
    pct_of_total: float


class TimelinePoint(BaseModel):
    date: str   # YYYY-MM-DD
    count: int
