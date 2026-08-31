"""Rotation utilities with matching NumPy and PyTorch APIs."""

from . import numpy, se3_numpy

try:
    from . import torch, se3_torch
except ImportError:  # PyTorch is an optional dependency.
    torch = None  # type: ignore[assignment]
    se3_torch = None  # type: ignore[assignment]

__all__ = ["numpy", "torch", "se3_numpy", "se3_torch"]
__version__ = "0.1.0"
