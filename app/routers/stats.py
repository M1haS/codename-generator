from collections import defaultdict
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.models import Codename, CodenameStatus
from app.schemas.schemas import StyleStats, TimelinePoint

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/styles", response_model=List[StyleStats])
async def style_breakdown(db: AsyncSession = Depends(get_db)):
    """Usage stats broken down by generation style."""
    result = await db.execute(select(Codename))
    all_codenames = result.scalars().all()

    total = len(all_codenames)
    if total == 0:
        return []

    by_style: dict = defaultdict(lambda: {"total": 0, "active": 0, "retired": 0})
    for cn in all_codenames:
        s = cn.style.value
        by_style[s]["total"] += 1
        if cn.status == CodenameStatus.ACTIVE:
            by_style[s]["active"] += 1
        elif cn.status == CodenameStatus.RETIRED:
            by_style[s]["retired"] += 1

    return [
        StyleStats(
            style=style,
            total_generated=data["total"],
            active=data["active"],
            retired=data["retired"],
            pct_of_total=round(data["total"] / total * 100, 2),
        )
        for style, data in sorted(by_style.items(), key=lambda x: -x[1]["total"])
    ]


@router.get("/timeline", response_model=List[TimelinePoint])
async def generation_timeline(db: AsyncSession = Depends(get_db)):
    """Daily generation rate as a time series."""
    result = await db.execute(
        select(
            func.date(Codename.generated_at).label("day"),
            func.count().label("count"),
        ).group_by(func.date(Codename.generated_at)).order_by("day")
    )
    return [TimelinePoint(date=str(row.day), count=row.count) for row in result.all()]


@router.get("/summary")
async def summary(db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count()).select_from(Codename))).scalar()
    active = (
        await db.execute(select(func.count()).where(Codename.status == CodenameStatus.ACTIVE))
    ).scalar()
    retired = (
        await db.execute(select(func.count()).where(Codename.status == CodenameStatus.RETIRED))
    ).scalar()
    recycled = (
        await db.execute(select(func.count()).where(Codename.status == CodenameStatus.RECYCLED))
    ).scalar()

    return {
        "total_generated": total,
        "active": active,
        "retired": retired,
        "recycled": recycled,
        "recycle_rate_pct": round(recycled / total * 100, 2) if total else 0,
    }
