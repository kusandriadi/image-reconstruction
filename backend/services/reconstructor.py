from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Callable, Optional

from PIL import Image

try:
    import torch
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False


class Reconstructor:
    def __init__(self, model_path: str):
        self.model_path = str(model_path)
        self.model_loaded = False
        self.model: Optional[object] = None
        # Device selection: env DEVICE or auto
        requested = os.getenv("DEVICE", None)
        if TORCH_AVAILABLE:
            if requested in ("cuda", "cpu"):
                if requested == "cuda" and not torch.cuda.is_available():
                    self.device = "cpu"
                else:
                    self.device = requested
            else:
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = "cpu"

    def _lazy_load(self, progress: Optional[Callable[[int, str], None]] = None):
        if self.model_loaded:
            return
        if progress:
            progress(5, "loading model")
        if TORCH_AVAILABLE and Path(self.model_path).exists():
            # Placeholder: user should adjust to their architecture
            try:
                if self.model_path.endswith(".pt"):
                    self.model = torch.jit.load(self.model_path, map_location=self.device)
                else:
                    self.model = torch.load(self.model_path, map_location=self.device)
            except Exception:
                # If loading fails, fall back to CPU attempt before giving up
                if self.device != "cpu":
                    try:
                        self.model = torch.load(self.model_path, map_location="cpu")
                        self.device = "cpu"
                    except Exception:
                        self.model = None
                else:
                    self.model = None
            if hasattr(self.model, "eval"):
                self.model.eval()
            if hasattr(self.model, "to"):
                try:
                    self.model = self.model.to(self.device)
                except Exception:
                    # keep as is
                    pass
        else:
            # Fallback: no real model, pass-through
            self.model = None
        if progress:
            progress(15, f"model ready on {self.device}")
        self.model_loaded = True

    def reconstruct(self, input_path: str, output_path: str, progress: Optional[Callable[[int, str], None]] = None, cancelled: Optional[Callable[[], bool]] = None):
        def step(pct: int, msg: str):
            if progress:
                progress(pct, msg)
            if cancelled and cancelled():
                raise Cancelled()

        self._lazy_load(progress)

        step(20, "reading input")
        img = Image.open(input_path).convert("RGB")

        step(35, "preprocessing")
        tensor = None
        if TORCH_AVAILABLE:
            import torchvision.transforms as T  # type: ignore
            transform = T.Compose([T.ToTensor()])
            tensor = transform(img).unsqueeze(0)
            try:
                tensor = tensor.to(self.device)
            except Exception:
                # if move fails, keep cpu
                pass

        step(70, "running model")
        if TORCH_AVAILABLE and self.model is not None and tensor is not None:
            with torch.no_grad():
                out = self.model(tensor)
            # Normalize output into image
            if isinstance(out, (list, tuple)):
                out = out[0]
            if hasattr(out, "detach"):
                out = out.detach().cpu().squeeze(0)
            out_img = T.ToPILImage()(out)
        else:
            # If no model available, simply return the input image (placeholder)
            out_img = img

        step(90, "writing output")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        out_img.save(output_path, format="PNG")

        step(100, "done")


class Cancelled(Exception):
    pass
