from __future__ import annotations

from enum import Enum


class CebStatus(Enum):
    """
    Status du compte
    """

    Indefini = 0
    Valide = 1
    EnCours = 2
    CompteEstBon = 3
    CompteApproche = 4
    Invalide = 5
