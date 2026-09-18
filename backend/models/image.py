from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, LargeBinary

from database import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=True)
    content_type = Column(String, nullable=True)
    data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
