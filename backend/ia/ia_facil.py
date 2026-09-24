from __future__ import annotations
import random
from typing import Any
from backend.constantes import ResultadoTiro
from backend.ia.ia_base import IABase
from backend.models.posicao import Posicao
from backend.models.tabuleiro import Tabuleiro

class IAFacil(IABase):

    def __init__(self, seed: int | None=None) -> None:
        self._rng = random.Random(seed)

    def escolher_jogada(self, tabuleiro_adversario: Tabuleiro) -> Posicao:
        disponiveis = tabuleiro_adversario.posicoes_nao_atacadas()
        if not disponiveis:
            raise ValueError('Não há posições disponíveis para ataque no tabuleiro adversário.')
        return self._rng.choice(disponiveis)

    def registrar_resultado(self, posicao: Posicao, resultado: ResultadoTiro, navio_afundado: Any | None) -> None:
        pass

    def reiniciar(self) -> None:
        pass
