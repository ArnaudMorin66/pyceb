import locale
import os
import platform
import subprocess
import sys
import time
from typing import List, Self

from PySide6.QtCore import Slot, Qt, QElapsedTimer, QModelIndex
from PySide6.QtGui import QIcon, QAction, QKeySequence, QCursor
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox,
                               QHBoxLayout, QComboBox, QSpinBox, QLayout,
                               QGridLayout, QLabel, QMenu,
                               QFileDialog, QSystemTrayIcon)

import ui.qceb_rcc  # noqa: F401
from ceb import CebStatus, CebTirage
from ui import QComboboxPlq, QSpinBoxSearch
from ui import QSolutionDialog
from ui import QSolutionsView
from ui import QThemeManager, Theme
from utils import singleton


@singleton
class QCeb(QWidget):
    """
    Classe principale pour l'interface utilisateur du jeu "Jeux du Compte est bon".
    """
    # _instance = None  #: Instance unique de QCeb.

    tirage: CebTirage  #:  Instance de CebTirage pour gérer le tirage actuel.

    plaques_inputs: List[QComboBox] = []  #: Liste des QComboBox pour les plaques.

    labels_results: List[QLabel] = []  #: Liste des QLabel pour afficher les résultats.

    search_input: QSpinBox  #: QSpinBox pour la valeur de recherche.

    solutions_table: QSolutionsView  #: QTableView pour afficher les solutions.

    context_menu: QMenu  #: Menu contextuel pour les actions de l'application.

    _tray_icon: QSystemTrayIcon  #: Icône de la barre d'état.

    # noinspection PyUnresolvedReferences
    # def __new__(cls, *args, **kwargs):
    #
    #     """Méthode spéciale pour créer une instance unique de la classe QCeb (singleton).
    #
    #     Cette méthode surcharge la méthode __new__ pour implémenter le patron de conception Singleton.
    #     Elle vérifie si une instance de la classe existe déjà. Si ce n'est pas le cas, elle crée une nouvelle instance
    #     à l'aide de la méthode __new__ de la superclasse et la stocke dans l'attribut de classe _instance.
    #     Dans tous les cas, elle retourne l'instance unique stockée dans _instance.
    #
    #     Args:
    #         klass: La classe pour laquelle une nouvelle instance doit être créée.
    #         *args: Arguments positionnels passés à la méthode __new__ de la superclasse.
    #         **kwargs: Arguments nommés passés à la méthode __new__ de la superclasse.
    #
    #     Returns:
    #         L'instance unique de la classe QCeb.
    #     """
    #     if cls._instance is None:
    #         cls._instance = super(QCeb, cls).__new__(cls, *args, **kwargs)
    #     return cls._instance

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

        self.tirageform_layout = QVBoxLayout()  # Crée un layout vertical pour l'interface utilisateur.
        self.add_inputs_layout()
        self.add_command_layout()
        self.add_result_layout()
        self.add_solutions_table()
        self.setLayout(self.tirageform_layout)  # Définit le layout principal de la fenêtre.
        self.set_context_menu()  # Configure le menu contextuel de l'application.

    def __call__(self):
        self.show()

    def set_context_menu(self):
        """
        Sets up the context menu with actions and their corresponding keyboard shortcuts.

        This method creates a QMenu and populates it with QAction items, each associated with a
        specific method and keyboard shortcut. Icons are also set for each action.
        """
        self.context_menu = QMenu()

        #:  List of actions with their names, shortcuts, methods, and icons
        actions = [
            ("Résoudre", "Ctrl+R", self.solve, "solve.png", False),
            ("Hasard", "Ctrl+H", self.random, "alea.png", False),
            ("Thème", "Ctrl+T", self.switch_theme, "theme.png", True),
            ("Sauvegarder", "Ctrl+S", self.save_results_dialog, "save.png", False),
            ("", "", None, "", False),
            ("Quitter", "Ctrl+Q", self.close, "quitter.png", False),
            ("", "", None, "", False),
            ("A propos", "Ctrl+A", self.apropos, "apropos.png", False)
        ]

        #: Iterate through the actions and add them to the context menu
        for name, shortcut, method, icon, check in actions:
            if name == "":
                self.context_menu.addSeparator()
                continue
            action = QAction(name, self)
            action.setIcon(QIcon(f":/images/{icon}"))
            if shortcut:
                action.setShortcut(QKeySequence(shortcut))
                action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
                self.addAction(action)
            if check:
                action.setCheckable(True)
                action.setChecked(True)
                action.toggled.connect(method)
            else:
                action.triggered.connect(method)
            self.context_menu.addAction(action)

        tray_icon = QSystemTrayIcon(self)
        tray_icon.setContextMenu(self.context_menu)
        tray_icon.setToolTip("Jeux du Compte est bon")

        tray_icon.activated.connect(self.tray_activate)

        tray_icon.setIcon(QIcon(":/images/apropos.png"))
        tray_icon.show()

    @Slot(QSystemTrayIcon.ActivationReason)
    def tray_activate(self, reason):
        """
        Gère l'activation de l'icône de la barre d'état système.

        Cette méthode affiche le menu contextuel lorsque l'icône de la barre d'état système est activée.

        Args:
            reason (QSystemTrayIcon.ActivationReason): La raison de l'activation.
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.context_menu.exec(QCursor.pos())

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
        if self.tirage.status not in [CebStatus.CompteEstBon, CebStatus.CompteApproche]:
            return

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
        theme_button.setToolTip("Basculer le thème")
        theme_button.setFixedWidth(40)
        theme_button.setCheckable(True)
        theme_button.setChecked(True)
        theme_button.toggled.connect(self.switch_theme)
        layout.addWidget(theme_button)

        self.tirageform_layout.addLayout(layout)
        return self

    def add_inputs_layout(self) -> Self:
        """
        Adds input fields layout for plaque selection.

        This method creates a horizontal box layout and populates it with six
        QComboBox widgets. Each combo box is configured to handle plaque selections
        with unique strings from a predefined list. The combo boxes are made editable
        and connected to the update_plaque method to handle changes in the text.
        Additionally, the created combo boxes are stored in a list attribute for
        further access. The search input field is added to the layout before integrating
        the complete layout into tirage form layout.

        Returns:
            Self: The instance of the current object.
        """
        layout = QHBoxLayout()

        for plq in self.tirage.plaques:
            combo_box = QComboboxPlq(plq)
            combo_box.currentTextChanged.connect(self.update_data)
            layout.addWidget(combo_box)
            self.plaques_inputs.append(combo_box)

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
        search_input = QSpinBoxSearch(self.tirage)
        search_input.valueChanged.connect(self.update_data)
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
        self.solutions_table = QSolutionsView(self.tirage)
        self.solutions_table.selectionModel().currentRowChanged.connect(self.selection_changed)
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
        results = [f"{str(self.tirage.status)}"]
        if self.tirage.status != CebStatus.Invalide:
            results += [
                f"Trouvé(s): {self.tirage.str_found}",
                f"{f'Ecart: {self.tirage.ecart}' if self.tirage.status == CebStatus.CompteApproche else ''}",
                f"Nombre de solutions: {self.tirage.count}",
                f"Durée: {duree / 1000.0:.3f} s"
            ]

        for ix, result in enumerate(results):
            self.labels_results[ix].setText(result)
            self.labels_results[ix].setStyleSheet(f"font-size: 14px; color:{color}; font-weight: bold;")
        self.setWindowTitle(" - ".join(results))

    @Slot(QModelIndex, )
    def selection_changed(self, current: QModelIndex, _):
        """
        Handles the selection change in a model view, triggered by a left mouse click with no keyboard modifiers. Opens a 
        QSolutionDialog for the selected solution in the tirage.

        Args:
            current (QModelIndex): The currently selected model index.
            _ (any): Unused placeholder parameter.
        """
        if (QApplication.mouseButtons() == Qt.MouseButton.LeftButton and
                (QApplication.keyboardModifiers() == Qt.KeyboardModifier.NoModifier)):
            QSolutionDialog(self.tirage.solutions[current.row()], self.tirage.status).exec()

    @Slot()
    def random(self):
        """
        Génère un tirage aléatoire et met à jour les entrées de l'interface utilisateur.

        Cette méthode appelle la méthode `random` de l'objet `tirage` pour générer un nouveau tirage aléatoire.
        Elle met ensuite à jour les QComboBox et le QSpinBox de l'interface utilisateur avec les nouvelles valeurs
        générées. Enfin, elle appelle la méthode `clear` pour réinitialiser l'état de l'interface utilisateur.
        """
        self.tirage.random()
        self.clear()

    # noinspection PyUnresolvedReferences
    @Slot()
    def update_data(self):
        """
        Met à jour la valeur d'une plaque spécifique en fonction de l'entrée utilisateur.

        Cette méthode est appelée lorsque le texte actuel d'une QComboBox change.
        Elle met à jour la valeur de la plaque correspondante dans l'objet `tirage`,
        réinitialise l'interface utilisateur et met à jour le layout des résultats si le statut du tirage est `Invalide`.
        """
        self.clear()
        if self.tirage.status == CebStatus.Invalide:
            self.set_result_layout(0)

    @Slot()
    def clear(self) -> None:
        """
        Réinitialise l'état du tirage et met à jour l'interface utilisateur.

        Cette méthode appelle la méthode `clear` de l'objet `tirage` pour réinitialiser l'état du tirage.
        Elle met ensuite à jour le modèle de données et efface le texte des labels de résultats.
        """
        # noinspection PyUnresolvedReferences
        self.solutions_table()
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

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        timer = QElapsedTimer()
        timer.start()
        self.tirage()  # Appelle la méthode de résolution
        self.set_result_layout(timer.elapsed())
        # noinspection PyUnresolvedReferences
        self.solutions_table()
        QApplication.restoreOverrideCursor()
        self.solutions_table.setFocus()
        if self.tirage.status in [CebStatus.CompteEstBon, CebStatus.CompteApproche]:
            QSolutionDialog(self.tirage.solutions[0], self.tirage.status).exec()

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

    @Slot()
    def switch_theme(self):
        """
        Bascule entre les thèmes clair et sombre.
        """
        QThemeManager().switch_theme()


def qceb_exec():
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
    app.setApplicationVersion("1.1")
    app.setOrganizationName("© Arnaud Morin")
    app.setWindowIcon(QIcon(":/images/apropos.png"))
    QThemeManager().theme = Theme.dark
    window = QCeb()
    window()
    sys.exit(app.exec())


if __name__ == "__main__":
    qceb_exec()
