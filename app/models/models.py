from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class CodenameStatus(PyEnum):
    ACTIVE = "active"
    RETIRED = "retired"
    RESERVED = "reserved"
    RECYCLED = "recycled"


class GenerationStyle(PyEnum):
    MILITARY = "military"
    NATURE = "nature"
    ABSTRACT = "abstract"
    COSMIC = "cosmic"


class Namespace(Base):
    __tablename__ = "namespaces"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(80), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    owner = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    codenames = relationship("Codename", back_populates="namespace", cascade="all, delete-orphan")


class Codename(Base):
    __tablename__ = "codenames"

    id = Column(Integer, primary_key=True, index=True)
    namespace_id = Column(Integer, ForeignKey("namespaces.id"), nullable=False)

    value = Column(String(200), nullable=False, index=True)
    style = Column(Enum(GenerationStyle), nullable=False)
    language = Column(String(5), default="en")
    word_count = Column(Integer, default=2)
    separator = Column(String(20), default="space")
    status = Column(Enum(CodenameStatus), default=CodenameStatus.ACTIVE)

    # What this codename is assigned to
    assigned_to = Column(String(300), nullable=True)   # e.g. "user:42", "project:alpha"
    assigned_at = Column(DateTime, nullable=True)
    retired_at = Column(DateTime, nullable=True)

    # Re-usability
    use_count = Column(Integer, default=1)
    eligible_recycle_at = Column(DateTime, nullable=True)

    generated_at = Column(DateTime, default=datetime.utcnow, index=True)
    meta = Column(JSON, default=dict)

    namespace = relationship("Namespace", back_populates="codenames")
