from __future__ import annotations

from .cebbase import CebBase


class CebPlaque(CebBase):
    def __init__(self, v=0):
        super().__init__()
        self._value = v
        self.operations.extend([str(v)])
