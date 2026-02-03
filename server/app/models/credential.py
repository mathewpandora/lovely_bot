from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Credential(Base):
    __tablename__ = "credentials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    valentines_received: Mapped[list["Valentine"]] = relationship(
        "Valentine", back_populates="recipient", foreign_keys="Valentine.recipient_id"
    )
