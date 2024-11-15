from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QDialog, QGridLayout, QListWidget, QListWidgetItem


class SolutionDialog(QDialog):
    """
    Classe de boîte de dialogue pour afficher les solutions d'un tirage.

    Args:
        solution: La solution à afficher.
        status: Le statut du tirage.
    """

    def __init__(self, solution, status):
        """
        Initialise la boîte de dialogue avec la solution et le statut donnés.

        Args:
            solution: La solution à afficher.
            status: Le statut du tirage.
        """
        super().__init__()
        self.setWindowTitle(str(status))
        self.setModal(True)
        layout = QGridLayout()
        list_widget = QListWidget(self)
        list_widget.setAlternatingRowColors(True)
        list_widget.setItemAlignment(Qt.AlignmentFlag.AlignHCenter)
        for operation in solution.operations:
            item = QListWidgetItem(operation)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            list_widget.addItem(item)
        list_widget.mousePressEvent = self.mousePressEvent
        layout.addWidget(list_widget)
        self.setLayout(layout)
        #: Ajouter un timer pour fermer la boîte de dialogue après 5 secondes
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.accept)
        self.timer.start(5000)

    def mousePressEvent(self, event):
        """
        Gère l'événement de clic de souris pour fermer la boîte de dialogue.

        Args:
            event (QMouseEvent): L'événement de clic de souris.
        """
        self.accept()
