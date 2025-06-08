"""
Avatar upload and processing service for high-resolution avatar management.
Supports Full HD (1920x1080) and 8K (7680x4320) resolutions.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps

from app.core.config import settings


class AvatarService:
    """Service for handling avatar uploads and multi-resolution processing."""

    SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    RESOLUTIONS = [
        (100, 100),      # Thumbnail
        (400, 400),      # Profile card
        (1920, 1080),    # Full HD
        (7680, 4320),    # 8K
    ]

    def __init__(self) -> None:
        try:
            upload_base = Path(settings.UPLOAD_DIR)
        except (AttributeError, PermissionError):
            upload_base = Path(__file__).parent.parent.parent.parent / "uploads"

        self.upload_dir = upload_base / "avatars"

        try:
            self.upload_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            pass

    async def upload_avatar(self, user_id: int, file: UploadFile) -> dict[str, Any]:
        """
        Upload and process avatar image into multiple resolutions.

        Args:
            user_id: ID of the user uploading the avatar
            file: Uploaded image file

        Returns:
            Dictionary with avatar_url, resolutions, file_size, and upload_timestamp

        Raises:
            HTTPException: If file validation or processing fails
        """
        await self._validate_file(file)

        user_dir = self.upload_dir / str(user_id)
        user_dir.mkdir(exist_ok=True)

        await file.seek(0)

        try:
            with Image.open(file.file) as img:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                img = ImageOps.exif_transpose(img)

                generated_files = []
                total_size = 0

                for width, height in self.RESOLUTIONS:
                    if img is not None:
                        processed_img = self._resize_and_optimize(img.copy(), width, height)
                    else:
                        continue
                    filename = f"avatar_{width}x{height}.jpg"
                    file_path = user_dir / filename

                    processed_img.save(
                        file_path,
                        "JPEG",
                        quality=95,
                        optimize=True,
                        progressive=True
                    )

                    file_size = file_path.stat().st_size
                    total_size += file_size
                    generated_files.append(f"{width}x{height}")

                base_url = f"/uploads/avatars/{user_id}/avatar_400x400.jpg"

                return {
                    "avatar_url": base_url,
                    "resolutions": generated_files,
                    "file_size": total_size,
                    "upload_timestamp": datetime.utcnow()
                }

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to process image: {str(e)}"
            ) from e

    async def delete_avatar(self, user_id: int) -> bool:
        """
        Delete all avatar files for a user.

        Args:
            user_id: ID of the user

        Returns:
            True if deletion was successful
        """
        user_dir = self.upload_dir / str(user_id)

        if not user_dir.exists():
            return True

        try:
            for file_path in user_dir.glob("avatar_*.jpg"):
                file_path.unlink()

            if not any(user_dir.iterdir()):
                user_dir.rmdir()

            return True

        except Exception:
            return False

    def get_avatar_url(self, user_id: int, resolution: str = "400x400") -> str | None:
        """
        Get avatar URL for specific resolution.

        Args:
            user_id: ID of the user
            resolution: Desired resolution (e.g., "400x400", "1920x1080")

        Returns:
            Avatar URL or None if not found
        """
        file_path = self.upload_dir / str(user_id) / f"avatar_{resolution}.jpg"

        if file_path.exists():
            return f"/uploads/avatars/{user_id}/avatar_{resolution}.jpg"

        return None

    def list_available_resolutions(self, user_id: int) -> list[str]:
        """
        List all available resolutions for a user's avatar.

        Args:
            user_id: ID of the user

        Returns:
            List of available resolutions
        """
        user_dir = self.upload_dir / str(user_id)

        if not user_dir.exists():
            return []

        resolutions = []
        for file_path in user_dir.glob("avatar_*.jpg"):
            filename = file_path.stem
            resolution = filename.replace("avatar_", "")
            resolutions.append(resolution)

        return sorted(resolutions)

    async def _validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file format and size."""
        file_size = 0
        chunk_size = 8192

        while chunk := await file.read(chunk_size):
            file_size += len(chunk)
            if file_size > self.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size is {self.MAX_FILE_SIZE // (1024*1024)}MB"
                )

        await file.seek(0)

        try:
            with Image.open(file.file) as img:
                if img.format not in self.SUPPORTED_FORMATS:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unsupported format. Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
                    )

                if img.width < 100 or img.height < 100:
                    raise HTTPException(
                        status_code=400,
                        detail="Image must be at least 100x100 pixels"
                    )

        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=400,
                detail="Invalid image file"
            ) from e

        await file.seek(0)

    def _resize_and_optimize(self, img: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """
        Resize image to target dimensions with smart cropping and optimization.

        Args:
            img: Source image
            target_width: Target width
            target_height: Target height

        Returns:
            Resized and optimized image
        """
        source_ratio = img.width / img.height
        target_ratio = target_width / target_height

        if source_ratio > target_ratio:
            new_width = int(img.height * target_ratio)
            left = (img.width - new_width) // 2
            img = img.crop((left, 0, left + new_width, img.height))
        elif source_ratio < target_ratio:
            new_height = int(img.width / target_ratio)
            top = (img.height - new_height) // 2
            img = img.crop((0, top, img.width, top + new_height))

        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

        from PIL import ImageFilter
        img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))

        return img


avatar_service: AvatarService = AvatarService()
