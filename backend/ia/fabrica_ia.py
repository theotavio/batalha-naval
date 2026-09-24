from __future__ import annotations
from backend.constantes import DificuldadeIA
from backend.ia.ia_base import IABase
from backend.ia.ia_facil import IAFacil
from backend.ia.ia_media import IAMedia
from backend.ia.ia_dificil import IADificil
from backend.ia.ia_impossivel import IAImpossivel

class FabricaIA:

    @staticmethod
    def criar(dificuldade: DificuldadeIA | str, seed: int | None=None) -> IABase:
        if isinstance(dificuldade, str):
            try:
                dificuldade = DificuldadeIA(dificuldade)
            except ValueError:
                dificuldade = DificuldadeIA.MEDIA
        if dificuldade == DificuldadeIA.FACIL:
            return IAFacil(seed=seed)
        elif dificuldade == DificuldadeIA.MEDIA:
            return IAMedia(seed=seed)
        elif dificuldade == DificuldadeIA.DIFICIL:
            return IADificil(seed=seed)
        elif dificuldade == DificuldadeIA.IMPOSSIVEL:
            return IAImpossivel(seed=seed)
        else:
            return IAMedia(seed=seed)
