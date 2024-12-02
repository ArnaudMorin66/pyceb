from PySide6.QtCore import QElapsedTimer, Qt
from PySide6.QtWidgets import QApplication

from ceb import CebTirage, CebStatus
from utils import ObservableBase


class QTirage(CebTirage, ObservableBase):
    """
    Represents a specialized drawable object in a user interface, inheriting
    behaviors from CebTirage and ObservableBase.

    The QTirage class encapsulates drawing operations and status handling
    within a graphical application. It extends CebTirage functionality by
    adding observable pattern support through ObservableBase. This class
    also manages a duration attribute that records the time taken by
    certain operations, typically used for performance monitoring. The
    class provides methods for solving a problem and clearing the state,
    with notifications sent to observers when these operations occur.

    Attributes:
        _duree: An integer representing the duration of an operation.

    Parameters:
        parent: Optional; The parent widget, if any, to which this object belongs.
    """
    _duree = 0

    def __init__(self, parent=None):
        super().__init__(parent)
        ObservableBase.__init__(self)

    @property
    def duree(self):
        return self._duree

    def solve(self) -> CebStatus:
        """
        Executes the 'solve' method, measures its execution time, and notifies observers
        of the status.

        The method overrides the cursor to indicate a busy state, measures the duration
        it takes to execute the 'solve' method from the superclass, restores the cursor
        once finished, and notifies observers of the computation status. The duration
        is stored in the '_duree' attribute for later reference.

        Returns:
            CebStatus: The status result from the 'solve' method execution.
        """
        self._duree = 0
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        timer = QElapsedTimer()
        timer.start()
        status = super().solve()
        self._duree = timer.elapsed()
        QApplication.restoreOverrideCursor()
        self._notify(self, status)
        return status

    def clear(self) -> CebStatus:
        """
        Clears the current state of the object by resetting attributes and notifying changes.

        This method overrides the clear method from the superclass. Upon execution, it resets
        the _duree attribute to zero and then calls the _notify method to signal any changes
        in the object’s state using the result from the superclass clear method.

        Returns
        -------
        Any
            The result of the superclass clear method, which indicates the status after clearing.

        """
        status = super().clear()
        self._duree = 0
        self._notify(self, status)
        return status
