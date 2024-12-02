from PySide6.QtCore import QElapsedTimer, Qt
from PySide6.QtWidgets import QApplication

from ceb import CebTirage, CebStatus


class QTirage(CebTirage):
    """
    Represents an extended version of CebTirage with timing abilities.

    This class is derived from CebTirage and adds functionality to keep
    track of the duration of solve operations. It uses Qt's timing mechanisms
    to measure the time taken for computation and provides an interface
    to retrieve the elapsed time in milliseconds. This class is particularly
    useful for applications where performance measurement is necessary for
    solve operations.
    """
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

    def solve(self) -> CebStatus:
        """
        Solve the given plaques and measure the time taken.

        :return: The status of the solve operation.
        """
        self._duree = 0
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        timer = QElapsedTimer()
        timer.start()
        status = super().solve()
        self._duree = timer.elapsed()
        QApplication.restoreOverrideCursor()
        return status

    def clear(self):
        """
        Clear the current state and reset the duration.
        """
        super().clear()
        self._duree = 0
