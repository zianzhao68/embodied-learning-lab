"""Robot kinematics utilities with matching NumPy and PyTorch APIs."""

from . import numpy

try:
    from . import torch
except ImportError:
    torch = None  # type: ignore[assignment]

__all__ = ["numpy", "torch"]
__version__ = "0.2.0"
