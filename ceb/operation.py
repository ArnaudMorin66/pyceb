from __future__ import annotations

from ceb.base import CebBase

Oper = "+" or "x" or "-" or "/"


class CebOperation(CebBase):

    def __init__(self, g: CebBase, op: Oper, d: CebBase):
        """
        definir une Opération
        @type g: CebBase
        @type op: str (+-x/)
        @type d: CebBase
        """
        super().__init__()
        if g.value < d.value:
            g, d = d, g

        match op:
            case "+":
                self._value = g.value + d.value
            case "-":
                self._value = g.value - d.value
            case "x":
                self._value = g.value * d.value if g.value > 1 and d.value > 1 else 0
            case "/" | ":":
                self._value = g.value // d.value \
                    if d.value > 1 and g.value % d.value == 0 else 0
            case _:
                self._value = 0
        if self._value != 0:
            self._operations.clear()
            if isinstance(g, CebOperation):
                self._operations.extend(g.operations)
            if isinstance(d, CebOperation):
                self.operations.extend(d.operations)
            self._operations.append(f"{g._value} {op} {d._value} = {self._value}")
