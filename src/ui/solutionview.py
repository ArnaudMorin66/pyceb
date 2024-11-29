from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QTableView, QHeaderView

from ceb.tirage import CebTirage
from ui.dialog import QSolutionDialog
from ui.model import QCebTirageModel


class QSolutionsView(QTableView):
    """
    A custom QTableView to display solutions for a given CebTirage.
    """

    _tirage: CebTirage

    def __init__(self, tirage: CebTirage, parent=None):
        """
        Initialize the QSolutionsView.

        Args:
            tirage (CebTirage): The CebTirage instance containing the solutions.
            parent: The parent widget, if any.
        """
        super(QSolutionsView, self).__init__(parent)
        self._tirage = tirage
        self.setModel(QCebTirageModel(tirage))
        self.setShowGrid(True)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


    def refresh(self):
        """
        Refresh the view by emitting the layoutChanged signal.
        """
        self.model().layoutChanged.emit()

    def keyPressEvent(self, event: QKeyEvent):
        """
        Handle key press events for the QSolutionsView.

        If the Enter key is pressed, it opens a SolutionDialog for the currently selected solution.
        Otherwise, it passes the event to the parent class.

        Args:
            event (QKeyEvent): The key event to handle.
        """
        if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter}:
            current_index = self.currentIndex()
            if current_index.isValid():
                QSolutionDialog(self._tirage.solutions[current_index.row()], self._tirage.status).exec()
            return
        super().keyPressEvent(event)
