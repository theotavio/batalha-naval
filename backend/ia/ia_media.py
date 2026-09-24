from __future__ import annotations
import random
from typing import Any
from backend.constantes import ResultadoTiro
from backend.ia.ia_base import IABase
from backend.models.posicao import Posicao
from backend.models.tabuleiro import Tabuleiro

class IAMedia(IABase):

    def __init__(self, seed: int | None=None) -> None:
        self._rng = random.Random(seed)
        self.fila_alvos: list[Posicao] = []
        self.acertos_atuais: list[Posicao] = []

    def reiniciar(self) -> None:
        self.fila_alvos.clear()
        self.acertos_atuais.clear()

    def escolher_jogada(self, tabuleiro_adversario: Tabuleiro) -> Posicao:
        self.fila_alvos = [p for p in self.fila_alvos if not tabuleiro_adversario.foi_atacada(p)]
        if self.fila_alvos:
            return self.fila_alvos.pop(0)
        disponiveis = tabuleiro_adversario.posicoes_nao_atacadas()
        if not disponiveis:
            raise ValueError('Nenhuma posição disponível.')
        return self._rng.choice(disponiveis)

    def registrar_resultado(self, posicao: Posicao, resultado: ResultadoTiro, navio_afundado: Any | None) -> None:
        if resultado == ResultadoTiro.ACERTO:
            self.acertos_atuais.append(posicao)
            vizinhas = posicao.obter_vizinhas_ortogonais()
            self._rng.shuffle(vizinhas)
            for viz in vizinhas:
                if viz not in self.fila_alvos:
                    self.fila_alvos.append(viz)
        elif resultado == ResultadoTiro.AFUNDADO:
            if navio_afundado is not None and hasattr(navio_afundado, 'posicoes'):
                posicoes_navio = set(navio_afundado.posicoes)
                self.acertos_atuais = [p for p in self.acertos_atuais if p not in posicoes_navio]
                self.fila_alvos = [p for p in self.fila_alvos if p not in posicoes_navio]
            else:
                self.acertos_atuais.clear()
                self.fila_alvos.clear()
