import sys
import time
from typing import List, Self

from PySide6.QtCore import Slot, Qt, QAbstractTableModel
from PySide6.QtGui import QKeyEvent, QColor
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox,
                               QHBoxLayout, QComboBox, QSpinBox, QLayout, QTableView,
                               QHeaderView, QGridLayout, QLabel)

from ceb import CebTirage, PLAQUESUNIQUES, CebStatus  # Assurez-vous que le module CebTirage est importé correctement
from theme import ThemeManager


class CebTirageModel(QAbstractTableModel):
    def __init__(self, tirage: CebTirage):
        """
        Initializes the model with the given tirage.

        Args:
            tirage (CebTirage): The tirage object containing the solutions.
        """
        super().__init__()
        self._tirage = tirage

    def rowCount(self, parent=None):
        """
        Returns the number of rows in the model.

        Args:
            parent (QModelIndex, optional): The parent index. Defaults to None.

        Returns:
            int: The number of rows.
        """
        return len(self._tirage.solutions)

    def columnCount(self, parent=None):
        """
        Returns the number of columns in the model.

        Args:
            parent (QModelIndex, optional): The parent index. Defaults to None.

        Returns:
            int: The number of columns.
        """
        return 5  # Nombre fixe de colonnes pour les opérations

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """
        Returns the data for the given index and role.

        Args:
            index (QModelIndex): The index of the item.
            role (Qt.ItemDataRole): The role for which the data is requested.

        Returns:
            Any: The data for the given index and role.
        """
        match role:
            case Qt.ItemDataRole.DisplayRole:
                solution = self._tirage.solutions[index.row()]
                if index.column() < len(solution.operations):
                    return solution.operations[index.column()]
            case Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignCenter
            case Qt.ItemDataRole.BackgroundRole:
                if index.row() % 2 == 1 \
                        and self._tirage.status in [CebStatus.CompteEstBon, CebStatus.CompteApproche]:
                    return QColor(
                        Qt.GlobalColor.darkGreen if self._tirage.status == CebStatus.CompteEstBon else Qt.GlobalColor.darkMagenta)
            case Qt.ItemDataRole.ForegroundRole:
                if index.row() % 2 == 1 \
                        and self._tirage.status in [CebStatus.CompteEstBon, CebStatus.CompteApproche]:
                    return QColor(Qt.GlobalColor.white)
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """
        Returns the header data for the given section and orientation.

        Args:
            section (int): The section number.
            orientation (Qt.Orientation): The orientation of the header (horizontal or vertical).
            role (Qt.ItemDataRole): The role for which the data is requested.

        Returns:
            Any: The data for the header, depending on the role.
        """
        match role:
            case Qt.ItemDataRole.DisplayRole:
                return ["Opération 1", "Opération 2", "Opération 3", "Opération 4", "Opération 5"][section] \
                    if orientation == Qt.Orientation.Horizontal else str(section + 1)
            case Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignCenter
            case Qt.ItemDataRole.BackgroundRole:
                return QColor(
                    Qt.GlobalColor.darkGreen if self._tirage.status == CebStatus.CompteEstBon
                    else Qt.GlobalColor.darkMagenta if self._tirage.status == CebStatus.CompteApproche
                    else Qt.GlobalColor.lightGray
                )

            case Qt.ItemDataRole.ForegroundRole:
                return QColor(Qt.GlobalColor.white \
                                  if self._tirage.status in [CebStatus.CompteEstBon, CebStatus.CompteApproche] \
                                  else Qt.GlobalColor.black)

        return None

    def update_data(self):
        """
        Émet un signal pour réinitialiser le modèle de données.

        Cette méthode émet le signal `modelReset` pour indiquer que les données du modèle ont été mises à jour
        et que la vue associée doit être réinitialisée pour refléter les nouvelles données.
        """
        self.modelReset.emit()



class CebMainTirage(QWidget):
    """
    Classe principale pour l'interface utilisateur du jeu "Jeux du Compte est bon".

    Attributs:
        tirage (CebTirage): Instance de CebTirage pour gérer le tirage actuel.
        _plaques_inputs (List[QComboBox]): Liste des QComboBox pour les plaques.
        _labels_results (List[QLabel]): Liste des QLabel pour afficher les résultats.
        _search_input (QSpinBox): QSpinBox pour la valeur de recherche.
        _solutions_table (QTableView): QTableView pour afficher les solutions.
        _data_model (CebTirageModel): Modèle de données pour le QTableView.
    """
    tirage = CebTirage()
    _plaques_inputs: List[QComboBox] = []
    _labels_results: List[QLabel] = []
    _search_input: QSpinBox
    _solutions_table: QTableView
    _data_model: CebTirageModel

    def __init__(self):
        """
        Initialise l'interface principale du jeu "Jeux du Compte est bon".

        Cette méthode configure la fenêtre principale, initialise le gestionnaire de thème,
        et ajoute les différents layouts pour les entrées, commandes, résultats et solutions.
        """
        super().__init__()
        self.setWindowTitle("Jeux du Compte est bon")
        self.setMinimumSize(800, 600)
        self.theme_manager = ThemeManager(self)
        self.tirageform_layout = QVBoxLayout()
        self.add_inputs_layout() \
            .add_command_layout() \
            .add_result_layout() \
            .add_solutions_table()
        self.setLayout(self.tirageform_layout)

    def keyPressEvent(self, event: QKeyEvent):
        """
        Gère les événements de pression de touche pour le widget.

        Cette méthode remplace le gestionnaire d'événements de pression de touche par défaut
        pour fournir un comportement personnalisé pour des combinaisons de touches spécifiques
        lorsque le statut du tirage n'est pas `EnCours`.

        Args:
            event (QKeyEvent): L'événement de pression de touche à gérer.
        """
        if self.tirage.status == CebStatus.EnCours:
            return
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_R:
                self.solve()
            elif event.key() == Qt.Key.Key_H:
                self.random()
            elif event.key() == Qt.Key.Key_C:
                self.clear()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def add_command_layout(self) -> Self:
        """
        Ajoute un layout de commandes avec des boutons pour résoudre, générer un tirage aléatoire et basculer le thème.

        Returns:
            Self: L'instance actuelle de `CebMainTirage`.
        """
        layout = QHBoxLayout()
        solve_button = QPushButton("Résoudre", self)
        solve_button.clicked.connect(self.solve)
        layout.addWidget(solve_button)

        random_button = QPushButton("Hasard", self)
        random_button.clicked.connect(self.random)
        layout.addWidget(random_button)

        toggle_button = QPushButton("Thème Sombre", self)
        toggle_button.setCheckable(True)
        toggle_button.setChecked(True)
        toggle_button.clicked.connect(self.toggle_mode)
        layout.addWidget(toggle_button)

        self.tirageform_layout.addLayout(layout)
        return self

    def add_inputs_layout(self) -> Self:
        """
        Ajoute un layout horizontal contenant des QComboBox pour les plaques et un QSpinBox pour la recherche.

        Returns:
            Self: L'instance actuelle de `CebMainTirage`.
        """
        def add_combobox(index: int) -> QLayout:
            """
            Ajoute une QComboBox pour une plaque spécifique au layout.

            Args:
                index (int): L'index de la plaque à ajouter.

            Returns:
                QLayout: Le layout mis à jour avec la QComboBox ajoutée.
            """
            combo_box = QComboBox()
            combo_box.addItems([str(x) for x in PLAQUESUNIQUES])
            combo_box.setCurrentText(str(self.tirage.plaques[index]))
            combo_box.currentTextChanged.connect(self.clear)
            layout.addWidget(combo_box)
            self._plaques_inputs.append(combo_box)
            return layout

        layout = QHBoxLayout()
        for i in range(6):
            add_combobox(i)
        self.add_search_input(layout)
        self.tirageform_layout.addLayout(layout)
        return self

    def add_search_input(self, layout) -> QLayout:
        """
        Ajoute un QSpinBox pour la recherche au layout donné.

        Args:
            layout (QLayout): Le layout auquel ajouter le QSpinBox.

        Returns:
            QLayout: Le layout mis à jour avec le QSpinBox ajouté.
        """
        search_input = QSpinBox()
        search_input.setMinimum(100)
        search_input.setMaximum(999)
        search_input.setValue(self.tirage.search)
        search_input.valueChanged.connect(self.clear)
        layout.addWidget(search_input)
        self._search_input = search_input
        return layout

    def add_solutions_table(self) -> Self:
        """
        Ajoute un tableau pour afficher les solutions du tirage.

        Cette méthode crée un `QTableView` pour afficher les solutions du tirage,
        initialise le modèle de données `CebTirageModel` avec le tirage actuel,
        et configure le tableau pour afficher les données correctement.

        Returns:
            Self: L'instance actuelle de `CebMainTirage`.
        """
        self._solutions_table = QTableView()
        self._data_model = CebTirageModel(self.tirage)
        self._solutions_table.setModel(self._data_model)
        self._solutions_table.setShowGrid(True)
        self._solutions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tirageform_layout.addWidget(self._solutions_table)
        return self

    def add_result_layout(self) -> Self:
        """
        Ajoute un layout de résultats avec des labels pour afficher les informations du tirage.

        Returns:
            Self: L'instance actuelle de `CebMainTirage`.
        """
        layout = QGridLayout()
        for i in range(2):
            for j in range(3):
                label = QLabel("")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet("font-size: 14px; font-weight: bold;")
                self._labels_results.append(label)
                layout.addWidget(label, i, j)
        self.tirageform_layout.addLayout(layout)
        return self

    def clear_result_layout(self):
        """
           Efface le texte de tous les labels dans le layout des résultats.

           Cette méthode parcourt tous les labels stockés dans l'attribut `_labels_results`
           et réinitialise leur texte à une chaîne vide.
           """
        for label in self._labels_results:
            label.setText("")

    def set_result_layout(self, duree: float):
        """
        Met à jour le layout des résultats avec les informations du tirage actuel.

        Args:
            duree (float): La durée de la résolution en secondes.
        """
        color = {
            CebStatus.CompteEstBon: "green",
            CebStatus.CompteApproche: "magenta",
            CebStatus.Invalide: "red"
        }.get(self.tirage.status, "black")

        results = [
            f"{self.tirage.status.name}",
            f"Trouvé: {self.tirage.found}",
            f"Ecart: {self.tirage.diff}",
            f"Nb solutions: {self.tirage.count}",
            f"Durée: {duree:.3f} s"
        ]

        for ix, result in enumerate(results):
            self._labels_results[ix].setText(result)
            self._labels_results[ix].setStyleSheet(f"font-size: 14px; color:{color}; font-weight: bold;")


    @Slot()
    def random(self):
        """
        Génère un tirage aléatoire et met à jour les entrées de l'interface utilisateur.

        Cette méthode appelle la méthode `random` de l'objet `tirage` pour générer un nouveau tirage aléatoire.
        Elle met ensuite à jour les QComboBox et le QSpinBox de l'interface utilisateur avec les nouvelles valeurs
        générées. Enfin, elle appelle la méthode `clear` pour réinitialiser l'état de l'interface utilisateur.
        """
        self.tirage.random()

        for i, x in enumerate(self.tirage.plaques):
            self._plaques_inputs[i].setCurrentText(str(x))

        self._search_input.setValue(self.tirage.search)
        self.clear()


    @Slot()
    def clear(self):
        """
        Réinitialise l'état du tirage et met à jour l'interface utilisateur.

        Cette méthode appelle la méthode `clear` de l'objet `tirage` pour réinitialiser l'état du tirage.
        Elle met ensuite à jour le modèle de données et efface le texte des labels de résultats.
        """
        self.tirage.clear()
        self._data_model.update_data()
        self.clear_result_layout()

    @Slot()
    def solve(self):
        """
        Résout le tirage actuel et met à jour l'interface utilisateur avec les résultats.

        Cette méthode effectue les étapes suivantes :
        1. Enregistre l'heure de début de la résolution.
        2. Met à jour les plaques et la valeur de recherche du tirage avec les valeurs actuelles des entrées utilisateur.
        3. Appelle la méthode `resolve` de l'objet `tirage` pour résoudre le tirage.
        4. Met à jour le layout des résultats avec la durée de la résolution.
        5. Met à jour le modèle de données pour refléter les nouvelles solutions.

        En cas d'exception, affiche un message d'erreur dans une boîte de dialogue.

        Raises:
            Exception: Si une erreur se produit lors de la résolution du tirage.
        """
        try:
            start = time.perf_counter()
            self.tirage.plaques = [int(k.currentText()) for k in self._plaques_inputs]
            self.tirage.search = self._search_input.value()
            self.tirage.resolve()
            self.set_result_layout(time.perf_counter() - start)
            self._data_model.update_data()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    @Slot()
    def toggle_mode(self):
        """
           Bascule le thème de l'application entre clair et sombre.

           Cette méthode appelle la méthode `switch_theme` de l'objet `theme_manager`
           pour changer le thème de l'application.
           """
        self.theme_manager.switch_theme()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    mainwindow = CebMainTirage()
    mainwindow.show()
    app.exec()

