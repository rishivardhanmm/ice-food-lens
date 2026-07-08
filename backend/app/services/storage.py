import os
import uuid

from PIL import Image as PILImage

from app.core.config import settings


def save_upload(file_bytes: bytes, original_filename: str) -> dict:
    os.makedirs(settings.upload_dir, exist_ok=True)
    ext = os.path.splitext(original_filename)[1] or ".jpg"
    stored_name = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(settings.upload_dir, stored_name)

    with open(filepath, "wb") as f:
        f.write(file_bytes)

    width = height = 0
    try:
        with PILImage.open(filepath) as img:
            width, height = img.size
    except Exception:
        pass

    return {"filepath": filepath, "stored_name": stored_name, "width": width, "height": height}
