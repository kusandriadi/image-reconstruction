from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set


@dataclass
class Config:
    base_dir: Path
    data_dir: Path
    uploads_dir: Path
    outputs_dir: Path
    models_dir: Path
    model_path: Path
    allowed_origins: List[str]
    max_upload_mb: float = 10.0
    allowed_mime: Set[str] = field(default_factory=lambda: {"image/png", "image/jpeg", "image/jpg", "image/webp"})
    allowed_ext: Set[str] = field(default_factory=lambda: {".png", ".jpg", ".jpeg", ".webp"})

    @property
    def max_upload_bytes(self) -> int:
        return int(self.max_upload_mb * 1024 * 1024)

    @staticmethod
    def from_env() -> "Config":
        base_dir = Path(__file__).resolve().parent
        data_dir = base_dir / "data"
        uploads_dir = data_dir / "uploads"
        outputs_dir = data_dir / "outputs"
        models_dir = data_dir / "models"

        for d in (uploads_dir, outputs_dir, models_dir):
            d.mkdir(parents=True, exist_ok=True)

        model_path = Path(os.getenv("MODEL_PATH", models_dir / "model.pth"))
        allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
        allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
        max_upload_mb = float(os.getenv("MAX_UPLOAD_MB", "10"))

        return Config(
            base_dir=base_dir,
            data_dir=data_dir,
            uploads_dir=uploads_dir,
            outputs_dir=outputs_dir,
            models_dir=models_dir,
            model_path=model_path,
            allowed_origins=allowed_origins or ["*"],
            max_upload_mb=max_upload_mb,
        )

