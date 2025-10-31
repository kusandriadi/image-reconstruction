"""Image reconstruction service using PyTorch models.

This module provides the Reconstructor class for loading and running PyTorch models
to reconstruct images. It supports both CPU and CUDA execution, lazy model loading,
progress callbacks, and cancellation handling.
"""
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
    """Image reconstruction engine using PyTorch models.

    This class handles loading and running PyTorch models for image reconstruction.
    It supports automatic device selection (CPU/CUDA), lazy model loading, progress
    tracking, and cancellation during processing.

    The model is loaded lazily on first use to avoid startup overhead. If PyTorch or
    the model file is not available, it falls back to pass-through mode (returns input).

    Attributes:
        model_path: Path to the PyTorch model file (.pt or .pth).
        model_loaded: Flag indicating if model has been loaded.
        model: Loaded PyTorch model instance (None if not loaded).
        device: Device being used for inference ('cpu' or 'cuda').

    Environment Variables:
        DEVICE: Force specific device ('cpu' or 'cuda'). Auto-detects if not set.

    Example:
        >>> reconstructor = Reconstructor(model_path="model.pth")
        >>> reconstructor.reconstruct(
        ...     input_path="input.png",
        ...     output_path="output.png",
        ...     progress=lambda pct, msg: print(f"{pct}%: {msg}")
        ... )
    """

    def __init__(self, model_path: str):
        """Initialize the reconstructor with model path and device selection.

        Args:
            model_path: Path to the PyTorch model file (.pt or .pth format).
        """
        self.model_path = str(model_path)
        self.model_loaded = False
        self.model: Optional[object] = None

        # Device selection: environment variable DEVICE or automatic
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
        """Lazily load the PyTorch model on first use.

        This method loads the model only when first needed, not during initialization.
        It tries to load the model on the configured device, falling back to CPU if
        loading fails. If PyTorch is not available or the model file doesn't exist,
        the reconstructor will operate in pass-through mode.

        Args:
            progress: Optional callback function(percent: int, message: str) for
                     reporting loading progress.

        Note:
            This method is called automatically by reconstruct() and should not be
            called directly.
        """
        if self.model_loaded:
            return
        if progress:
            progress(5, "loading model")
        if TORCH_AVAILABLE and Path(self.model_path).exists():
            # Load model based on file extension
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

            # Set model to evaluation mode and move to device
            if hasattr(self.model, "eval"):
                self.model.eval()
            if hasattr(self.model, "to"):
                try:
                    self.model = self.model.to(self.device)
                except Exception:
                    # Keep as is if transfer fails
                    pass
        else:
            # Fallback: no real model, will use pass-through mode
            self.model = None
        if progress:
            progress(15, f"model ready on {self.device}")
        self.model_loaded = True

    def reconstruct(
        self,
        input_path: str,
        output_path: str,
        progress: Optional[Callable[[int, str], None]] = None,
        cancelled: Optional[Callable[[], bool]] = None
    ):
        """Reconstruct an image using the loaded PyTorch model.

        This method processes an input image through the PyTorch model and saves
        the reconstructed result. It supports progress reporting and cancellation
        at various stages of processing.

        Processing stages:
        1. Model loading (0-15%)
        2. Reading input (15-20%)
        3. Preprocessing (20-35%)
        4. Model inference (35-70%)
        5. Writing output (70-90%)
        6. Done (90-100%)

        Args:
            input_path: Path to the input image file.
            output_path: Path where the reconstructed image will be saved.
            progress: Optional callback function(percent: int, message: str) for
                     reporting processing progress.
            cancelled: Optional callback function() -> bool that returns True if
                      processing should be cancelled.

        Raises:
            Cancelled: If the cancelled callback returns True during processing.
            IOError: If input file cannot be read.
            Exception: If model inference fails or output cannot be written.

        Example:
            >>> def track_progress(pct, msg):
            ...     print(f"Progress: {pct}% - {msg}")
            >>>
            >>> def is_cancelled():
            ...     return user_clicked_cancel
            >>>
            >>> reconstructor.reconstruct(
            ...     "input.jpg",
            ...     "output.png",
            ...     progress=track_progress,
            ...     cancelled=is_cancelled
            ... )
        """
        def step(pct: int, msg: str):
            """Internal helper to report progress and check cancellation."""
            if progress:
                progress(pct, msg)
            if cancelled and cancelled():
                raise Cancelled()

        # Load model lazily on first use
        self._lazy_load(progress)

        # Read and convert input image to RGB
        step(20, "reading input")
        img = Image.open(input_path).convert("RGB")

        # Preprocess image into tensor
        step(35, "preprocessing")
        tensor = None
        if TORCH_AVAILABLE:
            import torchvision.transforms as T  # type: ignore
            transform = T.Compose([T.ToTensor()])
            tensor = transform(img).unsqueeze(0)
            try:
                tensor = tensor.to(self.device)
            except Exception:
                # If device transfer fails, keep on CPU
                pass

        # Run model inference
        step(70, "running model")
        if TORCH_AVAILABLE and self.model is not None and tensor is not None:
            with torch.no_grad():
                out = self.model(tensor)
            # Normalize output into PIL Image
            if isinstance(out, (list, tuple)):
                out = out[0]
            if hasattr(out, "detach"):
                out = out.detach().cpu().squeeze(0)
            out_img = T.ToPILImage()(out)
        else:
            # Fallback: no model available, return input image (pass-through)
            out_img = img

        # Save reconstructed image
        step(90, "writing output")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        out_img.save(output_path, format="PNG")

        step(100, "done")


class Cancelled(Exception):
    """Exception raised when image reconstruction is cancelled by user.

    This exception is raised during reconstruction when the cancelled callback
    returns True, allowing graceful interruption of long-running operations.

    Example:
        >>> try:
        ...     reconstructor.reconstruct(..., cancelled=lambda: True)
        ... except Cancelled:
        ...     print("Reconstruction was cancelled")
    """
    pass
