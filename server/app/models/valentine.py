from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Valentine(Base):
    __tablename__ = "valentines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    track_link: Mapped[str] = mapped_column(String(2048), nullable=False)
    recipient_id: Mapped[int] = mapped_column(Integer, ForeignKey("credentials.id"), nullable=False, index=True)
    sender: Mapped[str | None] = mapped_column(Text, nullable=True)

    recipient: Mapped["Credential"] = relationship(
        "Credential", back_populates="valentines_received", foreign_keys=[recipient_id]
    )
