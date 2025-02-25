from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.models import Codename, Namespace, CodenameStatus
from app.schemas.schemas import GenerateRequest, GenerateResponse, CodenameOut, RetireRequest
from app.core.generator import generate_batch, CodenameExhaustedError
from app.config import settings

router = APIRouter(tags=["Codenames"])


async def _get_or_create_namespace(db: AsyncSession, slug: str) -> Namespace:
    result = await db.execute(select(Namespace).where(Namespace.slug == slug))
    ns = result.scalar_one_or_none()
    if not ns:
        ns = Namespace(slug=slug)
        db.add(ns)
        await db.flush()
    return ns


@router.post("/generate", response_model=GenerateResponse, status_code=status.HTTP_201_CREATED)
async def generate(payload: GenerateRequest, db: AsyncSession = Depends(get_db)):
    """Generate one or more unique codenames within a namespace."""
    ns = await _get_or_create_namespace(db, payload.namespace)

    # Collect existing active names in this namespace to prevent collisions
    existing_result = await db.execute(
        select(Codename.value).where(
            Codename.namespace_id == ns.id,
            Codename.status.in_([CodenameStatus.ACTIVE, CodenameStatus.RESERVED]),
        )
    )
    existing = {row[0] for row in existing_result.all()}

    try:
        names = generate_batch(
            count=payload.count,
            style=payload.style.value,
            lang=payload.language,
            word_count=payload.word_count,
            separator=payload.separator,
            existing_names=existing,
        )
    except CodenameExhaustedError as e:
        raise HTTPException(status_code=409, detail=str(e))

    now = datetime.utcnow()
    ids = []
    for name in names:
        cn = Codename(
            namespace_id=ns.id,
            value=name,
            style=payload.style,
            language=payload.language,
            word_count=payload.word_count,
            separator=payload.separator,
            status=CodenameStatus.ACTIVE,
            assigned_to=payload.assign_to,
            assigned_at=now if payload.assign_to else None,
            generated_at=now,
            meta=payload.meta,
        )
        db.add(cn)
        await db.flush()
        ids.append(cn.id)

    return GenerateResponse(
        codenames=names,
        style=payload.style.value,
        language=payload.language,
        namespace=payload.namespace,
        generated_count=len(names),
        ids=ids,
    )


@router.get("/codenames", response_model=List[CodenameOut])
async def list_codenames(
    namespace: Optional[str] = None,
    status_filter: Optional[CodenameStatus] = Query(None, alias="status"),
    style: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    q = select(Codename)
    if namespace:
        ns_result = await db.execute(select(Namespace).where(Namespace.slug == namespace))
        ns = ns_result.scalar_one_or_none()
        if ns:
            q = q.where(Codename.namespace_id == ns.id)
    if status_filter:
        q = q.where(Codename.status == status_filter)
    q = q.order_by(Codename.generated_at.desc()).offset(offset).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/codenames/{codename_id}", response_model=CodenameOut)
async def get_codename(codename_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Codename).where(Codename.id == codename_id))
    cn = result.scalar_one_or_none()
    if not cn:
        raise HTTPException(status_code=404, detail="Codename not found")
    return cn


@router.post("/codenames/{codename_id}/retire", response_model=CodenameOut)
async def retire_codename(
    codename_id: int,
    payload: RetireRequest,
    db: AsyncSession = Depends(get_db),
):
    """Retire a codename. It will be eligible for recycling after cooldown."""
    result = await db.execute(select(Codename).where(Codename.id == codename_id))
    cn = result.scalar_one_or_none()
    if not cn:
        raise HTTPException(status_code=404, detail="Codename not found")
    if cn.status == CodenameStatus.RETIRED:
        raise HTTPException(status_code=409, detail="Codename is already retired")

    now = datetime.utcnow()
    cn.status = CodenameStatus.RETIRED
    cn.retired_at = now
    cn.eligible_recycle_at = now + timedelta(days=settings.recycle_cooldown_days)
    if payload.reason:
        cn.meta = {**cn.meta, "retire_reason": payload.reason}

    await db.flush()
    await db.refresh(cn)
    return cn


@router.post("/codenames/{codename_id}/assign", response_model=CodenameOut)
async def assign_codename(
    codename_id: int,
    assign_to: str = Query(..., description="Entity identifier, e.g. 'user:42'"),
    db: AsyncSession = Depends(get_db),
):
    """Assign or re-assign a codename to an entity."""
    result = await db.execute(select(Codename).where(Codename.id == codename_id))
    cn = result.scalar_one_or_none()
    if not cn:
        raise HTTPException(status_code=404, detail="Codename not found")
    cn.assigned_to = assign_to
    cn.assigned_at = datetime.utcnow()
    await db.flush()
    await db.refresh(cn)
    return cn
