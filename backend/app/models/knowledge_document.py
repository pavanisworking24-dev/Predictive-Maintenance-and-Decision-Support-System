
import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    __table_args__ = (
        CheckConstraint(
            "ingestion_status IN ('PENDING', 'INGESTED', 'FAILED')",
            name="knowledge_documents_ingestion_status_check",
        ),
        UniqueConstraint(
            "title",
            "source",
            name="uq_knowledge_document_title_source",
        ),
        Index(
            "idx_knowledge_documents_type",
            "document_type",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    title: Mapped[str] = mapped_column(String(300), nullable=False)

    source: Mapped[str] = mapped_column(String(200), nullable=False)

    source_url: Mapped[str | None] = mapped_column(Text)

    document_type: Mapped[str | None] = mapped_column(String(100))

    description: Mapped[str | None] = mapped_column(Text)

    ingestion_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'PENDING'"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
