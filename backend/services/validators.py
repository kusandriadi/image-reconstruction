from __future__ import annotations

import io
from pathlib import Path
from typing import Set

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError


class UploadValidator:
    def __init__(self, allowed_mime: Set[str], allowed_ext: Set[str], max_bytes: int, uploads_dir: Path):
        self.allowed_mime = allowed_mime
        self.allowed_ext = allowed_ext
        self.max_bytes = max_bytes
        self.uploads_dir = uploads_dir

    @staticmethod
    def sanitize_filename(name: str, allowed_ext: Set[str]) -> str:
        base = Path(name).name
        safe = []
        for ch in base:
            safe.append(ch if (ch.isalnum() or ch in {'.', '_', '-'}) else '_')
        result = ''.join(safe)
        ext = Path(result).suffix.lower()
        if ext not in allowed_ext:
            result = Path(result).stem + '.png'
        return result

    def _check_size(self, content: bytes):
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        if len(content) > self.max_bytes:
            raise HTTPException(status_code=413, detail="File too large")

    def _check_type(self, content_type: str | None):
        if content_type and content_type not in self.allowed_mime:
            raise HTTPException(status_code=415, detail=f"Unsupported media type: {content_type}")

    def _check_image_decodable(self, content: bytes):
        try:
            Image.open(io.BytesIO(content)).verify()
        except UnidentifiedImageError:
            raise HTTPException(status_code=400, detail="Invalid image file")

    async def save(self, job_id: str, file: UploadFile) -> Path:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")
        self._check_type(file.content_type)
        content = await file.read()
        self._check_size(content)
        self._check_image_decodable(content)

        original_name = self.sanitize_filename(file.filename, self.allowed_ext)
        upload_path = self.uploads_dir / f"{job_id}_{original_name}"
        with open(upload_path, 'wb') as f:
            f.write(content)
        return upload_path

