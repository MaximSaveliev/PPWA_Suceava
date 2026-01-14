from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services.image_service import ImageService
from app.schemas.image import ImageOperation, ImageRecordResponse
from app.utils.dependencies import get_current_user
from app.models.user import User
from typing import List, Optional
import io

router = APIRouter(prefix="/images", tags=["Images"])


@router.post("/process", status_code=status.HTTP_200_OK)
def process_image(
    file: UploadFile = File(...),
    operation: ImageOperation = Form(...),
    width: Optional[int] = Form(None),
    height: Optional[int] = Form(None),
    x: Optional[int] = Form(None),
    y: Optional[int] = Form(None),
    angle: Optional[int] = Form(None),
    blur_radius: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    image_service = ImageService(db)
    
    kwargs = {
        'width': width,
        'height': height,
        'x': x,
        'y': y,
        'angle': angle,
        'blur_radius': blur_radius
    }
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    
    processed_data, filename, _ = image_service.process_image(
        user_id=current_user.id,
        file=file,
        operation=operation,
        **kwargs
    )
    
    return StreamingResponse(
        io.BytesIO(processed_data),
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename=processed_{filename}"}
    )


@router.get("/history", response_model=List[ImageRecordResponse])
def get_image_history(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    image_service = ImageService(db)
    return image_service.get_user_images(current_user.id, skip, limit)


@router.get("/{image_id}", status_code=status.HTTP_200_OK)
def get_processed_image(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    image_service = ImageService(db)
    image = image_service.get_image_by_id(image_id, current_user.id)
    
    if not image.image_data:
        return {"message": "Image data not stored"}
    
    return StreamingResponse(
        io.BytesIO(image.image_data),
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename={image.filename}"}
    )


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image_record(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    image_service = ImageService(db)
    image_service.delete_image(image_id, current_user.id)
