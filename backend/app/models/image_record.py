from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base


class ImageRecord(Base):
    __tablename__ = "image_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    operation = Column(String(20), nullable=False)
    original_size = Column(String(50))
    processed_size = Column(String(50))
    image_data = Column(LargeBinary, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    user = relationship("User", back_populates="image_records")
