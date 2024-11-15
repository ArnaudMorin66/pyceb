from PySide6.QtCore import QAbstractTableModel, Qt
from PySide6.QtGui import QColor

from ceb import CebTirage, CebStatus


class CebTirageModel(QAbstractTableModel):
    """
    Modèle de données pour afficher les solutions du tirage dans un QTableView.

    Attributes:
        _tirage (CebTirage): Instance de CebTirage contenant les solutions à afficher.
    """
    #: Instance de CebTirage contenant les solutions à afficher.
    _tirage: CebTirage

    def __init__(self, tirage: CebTirage):
        """
        Initialise le modèle de données avec le tirage donné.

        Args:
            tirage (CebTirage): Instance de CebTirage contenant les solutions à afficher.
        """
        super().__init__()
        self._tirage = tirage

    def rowCount(self, parent=None):
        """
        Retourne le nombre de lignes dans le modèle.

        Args:
            parent: Non utilisé.

        Returns:
            int: Le nombre de solutions dans le tirage.
        """
        return len(self._tirage.solutions)

    def columnCount(self, parent=None):
        """
        Retourne le nombre de colonnes dans le modèle.

        Args:
            parent: Non utilisé.

        Returns:
            int: Le nombre fixe de colonnes pour les opérations (5).
        """
        return 5  # Nombre fixe de colonnes pour les opérations

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """
        Retourne les données pour un index et un rôle donnés.

        Args:
            index (QModelIndex): L'index des données.
            role (Qt.ItemDataRole): Le rôle pour lequel les données sont demandées.

        Returns:
            QVariant: Les données pour l'index et le rôle donnés.
        """
        match role:
            case Qt.ItemDataRole.DisplayRole:
                solution = self._tirage.solutions[index.row()]
                if index.column() < len(solution.operations):
                    return solution.operations[index.column()]
            case Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignCenter
            case Qt.ItemDataRole.BackgroundRole:
                if index.row() % 2 == 1:
                    return QColor(
                        Qt.GlobalColor.darkGreen if self._tirage.status == CebStatus.CompteEstBon else QColor("saddlebrown"))
            case Qt.ItemDataRole.ForegroundRole:
                if index.row() % 2 == 1:
                    return QColor(Qt.GlobalColor.white)
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """
        Retourne les données d'en-tête pour une section, une orientation et un rôle donnés.

        Args:
            section (int): La section de l'en-tête.
            orientation (Qt.Orientation): L'orientation de l'en-tête.
            role (Qt.ItemDataRole): Le rôle pour lequel les données d'en-tête sont demandées.

        Returns:
            QVariant: Les données d'en-tête pour la section, l'orientation et le rôle donnés.
        """
        match role:
            case Qt.ItemDataRole.DisplayRole:
                return ["Opération 1", "Opération 2", "Opération 3", "Opération 4", "Opération 5"][section] \
                    if orientation == Qt.Orientation.Horizontal else str(section + 1)
            case Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignCenter
            case Qt.ItemDataRole.BackgroundRole:
                return QColor({
                                  CebStatus.CompteEstBon: Qt.GlobalColor.darkGreen,
                                  CebStatus.CompteApproche: "saddlebrown"
                              }.get(self._tirage.status, Qt.GlobalColor.black))

            case Qt.ItemDataRole.ForegroundRole:
                return QColor(Qt.GlobalColor.white \
                                  if self._tirage.status in [CebStatus.CompteEstBon, CebStatus.CompteApproche] \
                                  else Qt.GlobalColor.white)

        return None

    def refresh(self):
        """
        Rafraîchit le modèle de données en émettant un signal de réinitialisation.
        """
        self.modelReset.emit()
