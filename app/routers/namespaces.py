from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.models import Namespace, Codename, CodenameStatus
from app.schemas.schemas import NamespaceCreate, NamespaceOut, SaturationReport
from app.core.generator import pool_size

router = APIRouter(prefix="/namespaces", tags=["Namespaces"])


@router.get("/", response_model=List[NamespaceOut])
async def list_namespaces(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Namespace).where(Namespace.is_active == True))
    namespaces = result.scalars().all()
    out = []
    for ns in namespaces:
        count_result = await db.execute(
            select(func.count()).where(Codename.namespace_id == ns.id)
        )
        count = count_result.scalar() or 0
        ns_dict = {c.name: getattr(ns, c.name) for c in ns.__table__.columns}
        ns_dict["codename_count"] = count
        out.append(NamespaceOut(**ns_dict))
    return out


@router.post("/", response_model=NamespaceOut, status_code=status.HTTP_201_CREATED)
async def create_namespace(payload: NamespaceCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Namespace).where(Namespace.slug == payload.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Namespace '{payload.slug}' already exists")
    ns = Namespace(**payload.model_dump())
    db.add(ns)
    await db.flush()
    await db.refresh(ns)
    ns_dict = {c.name: getattr(ns, c.name) for c in ns.__table__.columns}
    ns_dict["codename_count"] = 0
    return NamespaceOut(**ns_dict)


@router.get("/{slug}", response_model=NamespaceOut)
async def get_namespace(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Namespace).where(Namespace.slug == slug))
    ns = result.scalar_one_or_none()
    if not ns:
        raise HTTPException(status_code=404, detail="Namespace not found")
    count_result = await db.execute(
        select(func.count()).where(Codename.namespace_id == ns.id)
    )
    count = count_result.scalar() or 0
    ns_dict = {c.name: getattr(ns, c.name) for c in ns.__table__.columns}
    ns_dict["codename_count"] = count
    return NamespaceOut(**ns_dict)


@router.get("/{slug}/saturation", response_model=SaturationReport)
async def get_saturation(
    slug: str,
    style: str = Query("military"),
    language: str = Query("en"),
    word_count: int = Query(2, ge=1, le=4),
    db: AsyncSession = Depends(get_db),
):
    """How saturated is the codename pool for a given namespace + style combo."""
    result = await db.execute(select(Namespace).where(Namespace.slug == slug))
    ns = result.scalar_one_or_none()
    if not ns:
        raise HTTPException(status_code=404, detail="Namespace not found")

    active_result = await db.execute(
        select(func.count()).where(
            Codename.namespace_id == ns.id,
            Codename.status == CodenameStatus.ACTIVE,
        )
    )
    active_count = active_result.scalar() or 0
    total_pool = pool_size(style, language, word_count)
    saturation = round((active_count / total_pool) * 100, 2) if total_pool else 100.0

    return SaturationReport(
        namespace=slug,
        style=style,
        language=language,
        word_count=word_count,
        pool_size=total_pool,
        active_count=active_count,
        saturation_pct=saturation,
        estimated_remaining=max(0, total_pool - active_count),
    )


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_namespace(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Namespace).where(Namespace.slug == slug))
    ns = result.scalar_one_or_none()
    if not ns:
        raise HTTPException(status_code=404, detail="Namespace not found")
    ns.is_active = False
