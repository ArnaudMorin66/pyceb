from __future__ import annotations

from .cebbase import *


class CebOperation(CebBase):

    def __init__(self, g: CebBase, op: str, d: CebBase):
        """

        @type g: object
        """
        super().__init__()
        if g._value < d._value:
            g, d = d, g

        match op:
            case "+":
                self._value = g._value + d._value
            case "-":
                self._value = g._value - d._value
            case "x":
                self._value = g._value * d._value if g._value > 1 and d._value > 1 else 0
            case "/":
                self._value = g._value // d._value \
                    if d._value > 1 and g._value % d._value == 0 else 0
            case _:
                self._value = 0
        if self._value != 0:
            self._operations.clear()
            if isinstance(g, CebOperation):
                self._operations.extend(g._operations)
            if isinstance(d, CebOperation):
                self.operations.extend(d.operations)
            self._operations.append(f"{g._value} {op} {d._value} = {self._value}")
