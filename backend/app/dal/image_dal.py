from sqlalchemy.orm import Session
from app.models.image_record import ImageRecord
from typing import Optional


class ImageDAL:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, image_id: int) -> Optional[ImageRecord]:
        return self.db.query(ImageRecord).filter(ImageRecord.id == image_id).first()

    def get_all_by_user_id(self, user_id: int, skip: int = 0, limit: int = 50) -> list[ImageRecord]:
        return self.db.query(ImageRecord).filter(
            ImageRecord.user_id == user_id
        ).order_by(ImageRecord.created_at.desc()).offset(skip).limit(limit).all()

    def create(
        self,
        user_id: int,
        filename: str,
        operation: str,
        original_size: str = None,
        processed_size: str = None,
        image_data: bytes = None
    ) -> ImageRecord:
        image_record = ImageRecord(
            user_id=user_id,
            filename=filename,
            operation=operation,
            original_size=original_size,
            processed_size=processed_size,
            image_data=image_data
        )
        self.db.add(image_record)
        self.db.commit()
        self.db.refresh(image_record)
        return image_record

    def delete(self, image_record: ImageRecord) -> None:
        self.db.delete(image_record)
        self.db.commit()

    def delete_by_id(self, image_id: int) -> bool:
        image_record = self.get_by_id(image_id)
        if image_record:
            self.delete(image_record)
            return True
        return False

    def count_by_user_id(self, user_id: int) -> int:
        return self.db.query(ImageRecord).filter(ImageRecord.user_id == user_id).count()
