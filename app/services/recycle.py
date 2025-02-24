"""
Recycle policy service.

Retired codenames become eligible for re-use after `recycle_cooldown_days`.
This service finds eligible codenames and marks them as RECYCLED,
re-entering them into the active pool.
"""

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Codename, CodenameStatus
from app.config import settings


async def recycle_eligible(db: AsyncSession) -> int:
    """
    Sweep retired codenames past cooldown and mark as RECYCLED.
    Returns count of recycled codenames.
    """
    now = datetime.utcnow()
    result = await db.execute(
        select(Codename).where(
            Codename.status == CodenameStatus.RETIRED,
            Codename.eligible_recycle_at <= now,
        )
    )
    candidates = result.scalars().all()
    for codename in candidates:
        codename.status = CodenameStatus.RECYCLED
        codename.use_count += 1
        codename.retired_at = None
        codename.assigned_to = None
    await db.flush()
    return len(candidates)


async def get_recycled_names_for_namespace(
    db: AsyncSession, namespace_id: int
) -> set[str]:
    """Return set of recycled (re-usable) codename values in a namespace."""
    result = await db.execute(
        select(Codename.value).where(
            Codename.namespace_id == namespace_id,
            Codename.status == CodenameStatus.RECYCLED,
        )
    )
    return {row[0] for row in result.all()}
