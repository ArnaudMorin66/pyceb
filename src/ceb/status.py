from __future__ import annotations

from enum import Enum


class CebStatus(Enum):
    """
    Enumération des statuts du compte.
    """

    Indefini = 0
    """Le statut du compte est indéfini."""

    Valide = 1
    """Le compte est valide."""

    EnCours = 2
    """Le compte est en cours de validation."""

    CompteEstBon = 3
    """Le compte est bon."""

    CompteApproche = 4
    """Le compte approche de la validation."""

    Invalide = 5
    """Le compte est invalide."""
