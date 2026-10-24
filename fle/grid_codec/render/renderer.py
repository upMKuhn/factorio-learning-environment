"""The renderer interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
from PIL import Image


class Renderer(ABC):
    """Turns a grid into an RGB image."""

    scale: int

    @abstractmethod
    def render(self, grid: np.ndarray) -> Image.Image: ...
