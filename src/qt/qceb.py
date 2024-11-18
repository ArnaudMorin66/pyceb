import locale
import os
import platform
import subprocess
import sys
import time
from typing import List, Self
from PySide6.QtCore import Slot, Qt, QElapsedTimer, QModelIndex, QStringListModel
from PySide6.QtGui import QKeyEvent, QIcon, QAction, QKeySequence, QCursor
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox,
                               QHBoxLayout, QComboBox, QSpinBox, QLayout, QTableView,
                               QHeaderView, QGridLayout, QLabel, QMenu,
                               QFileDialog, QSystemTrayIcon)
from zerovm_sphinx_theme import theme_path

from ceb import CebTirage, STRPLAQUESUNIQUES, CebStatus
import qt.qceb_rcc # noqab F401
from qt.dialog import SolutionDialog
from qt.model import CebTirageModel
from qt.theme import ThemeManager, Theme


class QCeb(QWidget):
    """
    Classe principale pour l'interface utilisateur du jeu "Jeux du Compte est bon".
    """


    tirage: CebTirage  #:  Instance de CebTirage pour gérer le tirage actuel.

    plaques_inputs: List[QComboBox] = [] #: Liste des QComboBox pour les plaques.

    labels_results: List[QLabel] = []   #: Liste des QLabel pour afficher les résultats.

    search_input: QSpinBox #: QSpinBox pour la valeur de recherche.

    solutions_table: QTableView #: QTableView pour afficher les solutions.

    data_model: CebTirageModel #: Modèle de données pour le QTableView.

    context_menu: QMenu #: Menu contextuel pour les actions de l'application.

    _tray_icon: QSystemTrayIcon #: Icône de la barre d'état.


    def __init__(self):
        """
        Initialise l'interface principale du jeu "Jeux du Compte est bon".

        Cette méthode configure la fenêtre principale, initialise le gestionnaire de thème,
        et ajoute les différents layouts pour les entrées, commandes, résultats et solutions.
        """
        super().__init__()
        self.tirage = CebTirage()  # Crée une instance de CebTirage pour gérer le tirage actuel.
        self.setWindowTitle("Jeux du Compte est bon")  # Définit le titre de la fenêtre principale.
        self.setMinimumSize(800, 400)  # Définit la taille minimale de la fenêtre.
        self.theme_manager = ThemeManager(self, Theme.dark)  # Crée un gestionnaire de thème.
        self.tirageform_layout = QVBoxLayout()  # Crée un layout vertical pour l'interface utilisateur.
        self.add_inputs_layout() \
            .add_command_layout() \
            .add_result_layout() \
            .add_solutions_table()  # Ajoute les différents layouts à la fenêtre principale.
        self.setLayout(self.tirageform_layout)  # Définit le layout principal de la fenêtre.
        self.update_inputs()  # Met à jour les entrées de l'interface utilisateur avec les valeurs actuelles du tirage.
        self.set_context_menu()  # Configure le menu contextuel de l'application.

    def set_context_menu(self):
        """
        Sets up the context menu with actions and their corresponding keyboard shortcuts.

        This method creates a QMenu and populates it with QAction items, each associated with a
        specific method and keyboard shortcut. Icons are also set for each action.
        """
        self.context_menu = QMenu()

        #:  List of actions with their names, shortcuts, methods, and icons
        actions = [
            ("Résoudre", "Ctrl+R", self.solve, "solve.png"),
            ("Hasard", "Ctrl+H", self.random, "alea.png"),
            ("Basculer Thème", "Ctrl+T", self.switch_theme, "theme.png"),
            ("Sauvegarder", "Ctrl+S", self.save_results_dialog, "save.png"),
            ("", "", None, ""),
            ("Quitter", "Ctrl+Q", self.close, "quitter.png"),
            ("", "", None, ""),
            ("A propos", "Ctrl+A", self.apropos, "apropos.png")
        ]

        #: Iterate through the actions and add them to the context menu
        for name, shortcut, method, icon in actions:
            if name == "":
                self.context_menu.addSeparator()
                continue
            action = QAction(name, self)
            action.setIcon(QIcon(f":/images/{icon}"))
            action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(method)
            self.context_menu.addAction(action)

        self._tray_icon = QSystemTrayIcon(self)
        self._tray_icon.setContextMenu(self.context_menu)
        self._tray_icon.setToolTip("Jeux du Compte est bon")

        self._tray_icon.activated.connect(self.tray_activate)

        self._tray_icon.setIcon(QIcon(":/images/apropos.png"))
        self._tray_icon.show()

    @Slot(QSystemTrayIcon.ActivationReason)
    def tray_activate(self, reason):
        """
        Gère l'activation de l'icône de la barre d'état système.

        Cette méthode affiche le menu contextuel lorsque l'icône de la barre d'état système est activée.

        Args:
            reason (QSystemTrayIcon.ActivationReason): La raison de l'activation.
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.context_menu.popup(QCursor.pos())

    def contextMenuEvent(self, event):
        """
        Gère l'événement de menu contextuel pour afficher un menu contextuel personnalisé.

        Args:
            event (QContextMenuEvent): L'événement de menu contextuel.
        """
        self.context_menu.exec(event.globalPos())

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
                if platform.system() == "Windows":
                    os.startfile(filename)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.call(("open", filename))
                else:  # Linux
                    subprocess.call(("xdg-open", filename))
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

        solve_button = QPushButton(QIcon(":/images/solve.png"), "Résoudre", self)
        solve_button.clicked.connect(self.solve)
        layout.addWidget(solve_button)

        random_button = QPushButton(QIcon(":/images/alea.png"), "Hasard", self)
        random_button.clicked.connect(self.random)
        layout.addWidget(random_button)

        save_button = QPushButton(QIcon(":/images/save.png"), "Sauvegarder", self)
        save_button.clicked.connect(self.save_results_dialog)
        layout.addWidget(save_button)

        theme_button = QPushButton(QIcon(":/images/theme.png"), "", self)
        theme_button.name = "theme_button"

        theme_button.setToolTip("Basculer le thème")
        theme_button.setFixedWidth(40)
        theme_button.setCheckable(True)
        theme_button.setChecked(True)

        theme_button.toggled.connect(self.switch_theme)
        layout.addWidget(theme_button)
        self.tirageform_layout.addLayout(layout)
        return self

    @Slot()
    def switch_theme(self):
        """
        Switches the theme between light and dark.

        This method toggles the theme between light and dark mode by setting the theme property
        of the ThemeManager to the opposite of the current theme.

        """
        self.theme_manager.theme = Theme.light if self.theme_manager.theme == Theme.dark else Theme.dark



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
            combo_box.setEditable(True)
            combo_box.currentTextChanged.connect(self.update_plaque)
            return combo_box

        cb_model = combobox_model()
        layout = QHBoxLayout()
        for i in range(6):
            cb = create_combobox(cb_model)
            layout.addWidget(cb)
            self.plaques_inputs.append(cb)

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
        self.search_input = search_input
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
        self.solutions_table = QTableView()
        self.data_model = CebTirageModel(self.tirage)
        self.solutions_table.setModel(self.data_model)
        self.solutions_table.setShowGrid(True)
        self.solutions_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.solutions_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.solutions_table.selectionModel().currentRowChanged.connect(self.selection_changed)
        self.solutions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tirageform_layout.addWidget(self.solutions_table)
        return self

    def add_result_layout(self) -> Self:
        """
        Ajoute un layout de résultats avec des labels pour afficher les informations du tirage.

        Returns:
            Self: L'instance actuelle de `CebMainTirage`.
        """
        layout = QGridLayout()
        for ligne in range(2):
            for colonne in range(3):
                label = QLabel("")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet("font-size: 14px; font-weight: bold;")
                self.labels_results.append(label)
                layout.addWidget(label, ligne, colonne)
        self.tirageform_layout.addLayout(layout)
        return self

    def clear_result_layout(self):
        """
           Efface le texte de tous les labels dans le layout des résultats.

           Cette méthode parcourt tous les labels stockés dans l'attribut `_labels_results`
           et réinitialise leur texte à une chaîne vide.
           """
        for label in self.labels_results:
            label.clear()
        self.setWindowTitle("Jeux du Compte est bon")

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
            f"{str(self.tirage.status)}",
            f"Trouvé(s): {self.tirage.str_found}",
            f"{ f'Ecart: {self.tirage.ecart}' if self.tirage.status == CebStatus.CompteApproche  else ''}",
            f"Nombre de solutions: {self.tirage.count}",
            f"Durée: {duree / 1000.0:.3f} s"
        ]

        for ix, result in enumerate(results):
            self.labels_results[ix].setText(result)
            self.labels_results[ix].setStyleSheet(f"font-size: 14px; color:{color}; font-weight: bold;")
        self.setWindowTitle( " - ".join(results) )

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
        for index, combo in enumerate(self.plaques_inputs):
            combo.setCurrentText(str(self.tirage.plaques[index]))
        self.search_input.setValue(self.tirage.search)
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
        self.tirage.plaques = [int(k.currentText()) for k in self.plaques_inputs]
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
        self.tirage.search = self.search_input.value()
        if self.tirage.status == CebStatus.Invalide:
            self.set_result_layout(0)

    @Slot()
    def clear(self) -> None:
        """
        Réinitialise l'état du tirage et met à jour l'interface utilisateur.

        Cette méthode appelle la méthode `clear` de l'objet `tirage` pour réinitialiser l'état du tirage.
        Elle met ensuite à jour le modèle de données et efface le texte des labels de résultats.
        """
        self.data_model.refresh()
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
        match self.tirage.status:
            case CebStatus.EnCours:
                return
            case CebStatus.CompteEstBon | CebStatus.CompteApproche | CebStatus.Invalide:
                self.random()
                return

        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

            timer = QElapsedTimer()
            timer.start()

            self.tirage.resolve()  # Appelle la méthode de résolution
            self.set_result_layout(timer.elapsed())
            self.data_model.refresh()
            QApplication.restoreOverrideCursor()

            if self.tirage.status in [CebStatus.CompteEstBon, CebStatus.CompteApproche]:
                SolutionDialog(self.tirage.solutions[0], self.tirage.status).exec()


        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))


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
    def exec():
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
        app.setWindowIcon(QIcon(":/images/apropos.png"))
        QCeb().show()
        sys.exit(app.exec())

if __name__ == "__main__":
    QCeb.exec()
