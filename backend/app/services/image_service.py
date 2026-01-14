from sqlalchemy.orm import Session
from app.dal.image_dal import ImageDAL
from app.services.subscription_service import SubscriptionService
from app.schemas.image import ImageOperation
from PIL import Image, ImageFilter
import io
from fastapi import HTTPException, status, UploadFile
from typing import Optional
from app.config.logging_config import get_logger

logger = get_logger("image_service")


class ImageService:
    def __init__(self, db: Session):
        self.db = db
        self.image_dal = ImageDAL(db)
        self.subscription_service = SubscriptionService(db)

    def process_image(
        self,
        user_id: int,
        file: UploadFile,
        operation: ImageOperation,
        **kwargs
    ):
        logger.info(f"Processing image for user {user_id}: {file.filename} - Operation: {operation.value}")
        self.subscription_service.check_operations_available(user_id)
        
        try:
            image_data = file.file.read()
            image = Image.open(io.BytesIO(image_data))
            original_size = f"{image.width}x{image.height}"
            
            if operation == ImageOperation.CROP:
                processed_image = self._crop_image(image, kwargs)
            elif operation == ImageOperation.GRAYSCALE:
                processed_image = self._grayscale_image(image)
            elif operation == ImageOperation.SEPIA:
                processed_image = self._sepia_image(image)
            elif operation == ImageOperation.RESIZE:
                processed_image = self._resize_image(image, kwargs)
            elif operation == ImageOperation.ROTATE:
                processed_image = self._rotate_image(image, kwargs)
            elif operation == ImageOperation.BLUR:
                processed_image = self._blur_image(image, kwargs)
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid operation")
            
            output = io.BytesIO()
            processed_image.save(output, format=image.format or 'PNG')
            processed_data = output.getvalue()
            processed_size = f"{processed_image.width}x{processed_image.height}"
            
            image_record = self.image_dal.create(
                user_id=user_id,
                filename=file.filename,
                operation=operation.value,
                original_size=original_size,
                processed_size=processed_size,
                image_data=processed_data
            )
            
            self.subscription_service.increment_operation_count(user_id)
            logger.info(f"Image processed successfully: {file.filename} ({original_size} -> {processed_size})")
            
            return processed_data, file.filename, image_record
            
        except Exception as e:
            logger.error(f"Image processing failed for user {user_id}: {file.filename} - {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Image processing failed: {str(e)}"
            )

    def get_user_images(self, user_id: int, skip: int = 0, limit: int = 50):
        return self.image_dal.get_all_by_user_id(user_id, skip, limit)

    def get_image_by_id(self, image_id: int, user_id: int):
        image = self.image_dal.get_by_id(image_id)
        if not image:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
        
        if image.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        return image

    def _crop_image(self, image: Image.Image, kwargs: dict) -> Image.Image:
        x = kwargs.get('x', 0)
        y = kwargs.get('y', 0)
        width = kwargs.get('width', image.width // 2)
        height = kwargs.get('height', image.height // 2)
        return image.crop((x, y, x + width, y + height))

    def _grayscale_image(self, image: Image.Image) -> Image.Image:
        return image.convert('L')

    def _sepia_image(self, image: Image.Image) -> Image.Image:
        grayscale = image.convert('L')
        sepia = Image.new('RGB', image.size)
        pixels = sepia.load()
        gray_pixels = grayscale.load()
        
        for i in range(image.width):
            for j in range(image.height):
                gray = gray_pixels[i, j]
                pixels[i, j] = (int(gray * 1.0), int(gray * 0.95), int(gray * 0.82))
        
        return sepia

    def _resize_image(self, image: Image.Image, kwargs: dict) -> Image.Image:
        width = kwargs.get('width', image.width // 2)
        height = kwargs.get('height', image.height // 2)
        return image.resize((width, height))

    def _rotate_image(self, image: Image.Image, kwargs: dict) -> Image.Image:
        angle = kwargs.get('angle', 90)
        return image.rotate(angle, expand=True)

    def _blur_image(self, image: Image.Image, kwargs: dict) -> Image.Image:
        radius = kwargs.get('blur_radius', 5)
        return image.filter(ImageFilter.GaussianBlur(radius))

    def delete_image(self, image_id: int, user_id: int) -> None:
        logger.info(f"Deleting image {image_id} for user {user_id}")
        image = self.image_dal.get_by_id(image_id)
        
        if not image:
            logger.warning(f"Image deletion failed - not found: {image_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image record not found")
        
        if image.user_id != user_id:
            logger.warning(f"Unauthorized image deletion attempt: user {user_id} tried to delete image {image_id}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this image")
        
        self.image_dal.delete(image)
        logger.info(f"Image deleted successfully: {image_id}")
