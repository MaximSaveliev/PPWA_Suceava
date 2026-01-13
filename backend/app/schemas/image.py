from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class ImageOperation(str, Enum):
    CROP = "crop"
    GRAYSCALE = "grayscale"
    SEPIA = "sepia"
    RESIZE = "resize"
    ROTATE = "rotate"
    BLUR = "blur"


class ImageProcessRequest(BaseModel):
    operation: ImageOperation
    width: Optional[int] = None
    height: Optional[int] = None
    x: Optional[int] = None
    y: Optional[int] = None
    angle: Optional[int] = None
    blur_radius: Optional[int] = None


class ImageRecordResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    operation: str
    original_size: Optional[str]
    processed_size: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
