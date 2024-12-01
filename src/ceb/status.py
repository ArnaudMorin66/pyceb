from __future__ import annotations

from enum import Enum, auto


class CebStatus(Enum):
    """
    Enumération des statuts du compte.
    """

    Indefini = auto()
    """Le statut du compte est indéfini."""

    Valide = auto()
    """Le compte est valide."""

    EnCours = auto()
    """Le compte est en cours de validation."""

    CompteEstBon = auto()
    """Le compte est bon."""

    CompteApproche = auto()
    """Le compte approche de la validation."""

    Invalide = auto()
    """Le compte est invalide."""

    def __str__(self) -> str:
        """
        Retourne une représentation en chaîne de caractères de l'état du compte.

        Returns:
            str: Une chaîne de caractères représentant l'état du compte.
        """
        return {
            CebStatus.Indefini: "Indéfini",
            CebStatus.Valide: "✔️ Valide",
            CebStatus.EnCours: "⚙️ En cours",
            CebStatus.CompteEstBon: "😀 Compte est bon",
            CebStatus.CompteApproche: "🙄 Compte approché",
            CebStatus.Invalide: " ❌ Invalide"
        }.get(self, "Inconnu")
