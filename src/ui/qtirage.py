from typing import List

from PySide6.QtCore import QElapsedTimer, Qt
from PySide6.QtWidgets import QApplication

from ceb import CebTirage, CebStatus, CebPlaque


class QTirage(CebTirage):
    _duree = 0

    def __init__(self, parent=None):
        """
        Initialize the QTirage instance.

        :param parent: The parent widget, if any.
        """
        super().__init__(parent)

    @property
    def duree(self):
        """
        Get the duration of the last solve operation.

        :return: The duration in milliseconds.
        """
        return self._duree

    def solve(self, plaques: List[int | CebPlaque] = (), search: int = 0) -> CebStatus:
        """
        Solve the given plaques and measure the time taken.

        :param plaques: A list of plaques to solve.
        :param search: The search parameter.
        :return: The status of the solve operation.
        """
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        timer = QElapsedTimer()
        timer.start()
        status = super().solve(plaques, search)
        self._duree = timer.elapsed()
        QApplication.restoreOverrideCursor()
        return status

    def clear(self):
        """
        Clear the current state and reset the duration.
        """
        self._duree = 0
        super().clear()