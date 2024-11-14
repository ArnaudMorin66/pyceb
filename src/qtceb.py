import locale
import os
import platform
import subprocess
import sys
import time
from typing import List, Self

from PySide6.QtCore import Slot, Qt, QAbstractTableModel, QElapsedTimer, QTimer, QModelIndex, QStringListModel
from PySide6.QtGui import QKeyEvent, QColor, QIcon, QAction, QKeySequence
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox,
                               QHBoxLayout, QComboBox, QSpinBox, QLayout, QTableView,
                               QHeaderView, QGridLayout, QLabel, QDialog, QListWidget, QListWidgetItem, QMenu,
                               QFileDialog)

import cebressources
from ceb import CebTirage, STRPLAQUESUNIQUES, CebStatus, \
    cebstatus_to_str  # Assurez-vous que le module CebTirage est importé correctement
from theme import ThemeManager


class CebTirageModel(QAbstractTableModel):
    """
    Modèle de données pour afficher les solutions du tirage dans un QTableView.

    Attributes:
        _tirage (CebTirage): Instance de CebTirage contenant les solutions à afficher.
    """

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
        #  ThemeManager(self)
        self.setWindowTitle(cebstatus_to_str(status))
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
        # Ajouter un timer pour fermer la boîte de dialogue après 5 secondes
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


class QtCeb(QWidget):
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
        self.setMinimumSize(800, 400)
        self.theme_manager = ThemeManager(self)
        self.tirageform_layout = QVBoxLayout()
        self.add_inputs_layout() \
            .add_command_layout() \
            .add_result_layout() \
            .add_solutions_table()
        self.setLayout(self.tirageform_layout)
        self.update_inputs()

    def contextMenuEvent(self, event):
        """
        Gère l'événement de menu contextuel pour afficher un menu contextuel personnalisé.

        Args:
            event (QContextMenuEvent): L'événement de menu contextuel.
        """
        context_menu = QMenu(self)

        actions = [
            ("Résoudre", "Ctrl+R", self.solve, "calculer.png"),
            ("Hasard", "Ctrl+H", self.random, "alea.png"),
            ("Basculer Thème", "Ctrl+T", self.toggle_mode, "yin-yang.png"),
            ("Sauvegarder", "Ctrl+S", self.save_results_dialog, "save.png"),
            ("", "", None, ""),
            ("Quitter", "Ctrl+Q", self.close, "quitter.png"),
            ("", "", None, ""),
            ("A propos", "Ctrl+A", self.apropos, "apropos.png")
        ]

        for name, shortcut, method, icon in actions:
            if name == "":
                context_menu.addSeparator()
                continue
            action = QAction(name, self)
            action.setIcon(QIcon(f":/images/{icon}"))
            action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(method)
            context_menu.addAction(action)

        context_menu.exec(event.globalPos())

    def save_results_dialog(self):
        """
        Ouvre une boîte de dialogue de sauvegarde pour enregistrer les résultats en JSON.
        """

        filename, _ = QFileDialog.getSaveFileName(self, "Sauvegarder les résultats", "",
                                                  "JSON Files (*.json);;XML Files (*.xml);; Pickle Files (*.pkl);; CSV Files (*.csv)",
                                                  )
        if filename:
            self.tirage.save(filename)
            try:
                if platform.system() == 'Windows':
                    os.startfile(filename)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(('open', filename))
                else:  # Linux
                    subprocess.call(('xdg-open', filename))
            except Exception as e:
                print(f"Erreur lors de l'ouverture du fichier : {e}")

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
            elif event.key() == Qt.Key.Key_A:
                self.apropos()
            elif event.key() == Qt.Key.Key_S:
                self.save_results_dialog()
            elif event.key() == Qt.Key.Key_Q:
                self.close()
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

        solve_button = QPushButton(QIcon(":/images/calculer.png"), "Résoudre", self)
        solve_button.clicked.connect(self.solve)
        layout.addWidget(solve_button)

        random_button = QPushButton(QIcon(":/images/alea.png"), "Hasard", self)
        random_button.clicked.connect(self.random)
        layout.addWidget(random_button)

        save_button = QPushButton(QIcon(":/images/save.png"), "Sauvegarder", self)
        save_button.clicked.connect(self.save_results_dialog)
        layout.addWidget(save_button)

        toggle_button = QPushButton(QIcon(":/images/yin-yang.png"), "Thème", self)
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

        def combobox_model():
            """
            Crée un modèle de données pour les QComboBox.

            Returns:
                QStringListModel: Le modèle de données pour les QComboBox.
            """
            model = QStringListModel()
            model.setStringList(STRPLAQUESUNIQUES)
            return model

        def create_combobox(model) -> QComboBox:
            """
            Crée une QComboBox pour une plaque spécifique et la configure avec le modèle donné.

            Args:
                model (QStringListModel): Le modèle de données pour la QComboBox.

         Returns:
                QLayout: Le layout mis à jour avec la QComboBox ajoutée.
            """
            combo_box = QComboBox()
            combo_box.setModel(model)
            combo_box.currentTextChanged.connect(self.update_plaque)
            return combo_box

        cb_model = combobox_model()
        layout = QHBoxLayout()
        for i in range(6):
            cb = create_combobox(cb_model)
            layout.addWidget(cb)
            self._plaques_inputs.append(cb)

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
        search_input.valueChanged.connect(self.update_search)
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
        self._solutions_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self._solutions_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._solutions_table.selectionModel().currentRowChanged.connect(self.selection_changed)
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
            label.clear()

    def set_result_layout(self, duree: int):
        """
        Met à jour le layout des résultats avec les informations du tirage actuel.

        Args:
            duree (int): La durée de la résolution en millisecondes.
        """
        color = {
            CebStatus.CompteEstBon: "green",
            CebStatus.CompteApproche: "saddlebrown",
            CebStatus.Invalide: "red"
        }.get(self.tirage.status, "black")

        results = [
            f"{cebstatus_to_str(self.tirage.status)}",
            f"Trouvé(s): {self.tirage.str_found}",
            f"Ecart: {self.tirage.ecart}",
            f"Nombre de solutions: {self.tirage.count}",
            f"Durée: {duree / 1000.0:.3f} s"
        ]

        for ix, result in enumerate(results):
            self._labels_results[ix].setText(result)
            self._labels_results[ix].setStyleSheet(f"font-size: 14px; color:{color}; font-weight: bold;")

    @Slot(QModelIndex, )
    def selection_changed(self, current: QModelIndex, _):
        """
        Slot appelé lorsque la sélection de ligne change dans le QTableView.

        Cette méthode affiche une boîte de dialogue avec les détails de la solution
        correspondant à la ligne actuellement sélectionnée.

        Args:
            current (QModelIndex): L'index de la ligne actuellement sélectionnée.
            _ (QModelIndex): L'index de la ligne précédemment sélectionnée.
        """
        if QApplication.mouseButtons() == Qt.MouseButton.LeftButton:
            SolutionDialog(self.tirage.solutions[current.row()], self.tirage.status).exec()

    @Slot()
    def random(self):
        """
        Génère un tirage aléatoire et met à jour les entrées de l'interface utilisateur.

        Cette méthode appelle la méthode `random` de l'objet `tirage` pour générer un nouveau tirage aléatoire.
        Elle met ensuite à jour les QComboBox et le QSpinBox de l'interface utilisateur avec les nouvelles valeurs
        générées. Enfin, elle appelle la méthode `clear` pour réinitialiser l'état de l'interface utilisateur.
        """
        self.tirage.random()
        self.update_inputs()

    def update_inputs(self):
        """
        Met à jour les entrées de l'interface utilisateur avec les valeurs actuelles du tirage.

        Cette méthode bloque temporairement les signaux de tous les widgets pour éviter des mises à jour
        redondantes, puis met à jour les QComboBox et le QSpinBox avec les valeurs actuelles du tirage.
        Enfin, elle réactive les signaux et appelle la méthode `clear` pour réinitialiser l'état de l'interface utilisateur.
        """
        self.block_allsignals()
        for index, combo in enumerate(self._plaques_inputs):
            combo.setCurrentText(str(self.tirage.plaques[index]))
        self._search_input.setValue(self.tirage.search)
        self.block_allsignals(False)
        self.clear()

    @staticmethod
    def block_allsignals(value: bool = True):
        """
        Bloque ou débloque les signaux de tous les widgets de l'application.

        Args:
            value (bool): Si True, bloque les signaux. Si False, débloque les signaux.
        """
        for widget in QApplication.allWidgets():
            widget.blockSignals(value)

    @Slot()
    def update_plaque(self):
        """
        Met à jour les plaques du tirage avec les valeurs actuelles des QComboBox.

        Cette méthode met à jour les plaques du tirage avec les valeurs actuelles des QComboBox
        stockées dans l'attribut `_plaques_inputs`.
        """
        self.clear()
        self.tirage.plaques = [int(k.currentText()) for k in self._plaques_inputs]
        if self.tirage.status == CebStatus.Invalide:
            self.set_result_layout(0)

    @Slot()
    def update_search(self):
        """
        Met à jour la valeur de recherche du tirage avec la valeur actuelle du QSpinBox.

        Cette méthode met à jour la valeur de recherche du tirage avec la valeur actuelle du QSpinBox
        stockée dans l'attribut `_search_input`.
        """
        self.clear()
        self.tirage.search = self._search_input.value()
        if self.tirage.status == CebStatus.Invalide:
            self.set_result_layout(0)

    @Slot()
    def clear(self):
        """
        Réinitialise l'état du tirage et met à jour l'interface utilisateur.

        Cette méthode appelle la méthode `clear` de l'objet `tirage` pour réinitialiser l'état du tirage.
        Elle met ensuite à jour le modèle de données et efface le texte des labels de résultats.
        """
        # self.tirage.clear()
        self._data_model.refresh()
        self.clear_result_layout()

    @Slot()
    def load_data(self):
        self.tirage.plaques = [int(k.currentText()) for k in self._plaques_inputs]
        self.tirage.search = self._search_input.value()

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
        match self.tirage.status:
            case CebStatus.EnCours:
                return
            case CebStatus.CompteEstBon | CebStatus.CompteApproche | CebStatus.Invalide:
                self.random()
                return

        try:
            timer = QElapsedTimer()
            timer.start()

            self.tirage.resolve()  # Appelle la méthode de résolution
            self.set_result_layout(timer.elapsed())
            self._data_model.refresh()

            if self.tirage.status in [CebStatus.CompteEstBon, CebStatus.CompteApproche]:
                SolutionDialog(self.tirage.solutions[0], self.tirage.status).exec()


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

    @Slot()
    def apropos(self):
        """
        Affiche une boîte de dialogue "A propos" avec des informations sur l'application.

        Cette méthode utilise `QMessageBox.about` pour afficher le nom de l'application,
        la version, l'auteur et la date actuelle.
        """
        QMessageBox.about(self, "A propos",
                          QApplication.applicationName() + " v" + QApplication.applicationVersion() + "\n" + "Auteur: " + QApplication.organizationName() + "\n" + "Date: " + time.strftime(
                              "%d/%m/%Y %H:%M:%S"))

    @staticmethod
    def run():
        """
        Initialise et exécute l'application principale.

        Cette fonction configure les paramètres régionaux, crée l'application principale,
        initialise les ressources, configure l'icône de la fenêtre, et affiche la fenêtre principale.
        Elle exécute ensuite la boucle d'événements de l'application.
        """
        locale.setlocale(locale.LC_NUMERIC, 'fr_FR.UTF-8')
        # Crée et exécute l'application principale
        app = QApplication(sys.argv)
        app.setApplicationName("Jeux du Compte est bon")
        app.setApplicationVersion("1.0")
        app.setOrganizationName("© Arnaud Morin")
        cebressources.qInitResources()
        app.setWindowIcon(QIcon(":/images/apropos.png"))
        mainwindow = QtCeb()
        mainwindow.show()
        app.exec()
        sys.exit(0)

if __name__ == "__main__":
    QtCeb.run()
