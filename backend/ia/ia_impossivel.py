from __future__ import annotations
import random
from typing import Any
from backend.constantes import ResultadoTiro, Orientacao, EstadoCelula
from backend.ia.ia_base import IABase
from backend.models.posicao import Posicao
from backend.models.navio import Navio
from backend.models.tabuleiro import Tabuleiro

class IAImpossivel(IABase):
    NOME_PADRAO = 'Marechal Anthony'

    def __init__(self, seed: int | None=None) -> None:
        self._rng = random.Random(seed)

    def reiniciar(self) -> None:
        pass

    def registrar_resultado(self, posicao: Posicao, resultado: ResultadoTiro, navio_afundado: Any | None) -> None:
        pass

    def escolher_jogada(self, tabuleiro_adversario: Tabuleiro) -> Posicao:
        alvos_garantidos: list[Posicao] = []
        for navio in tabuleiro_adversario.navios:
            if not navio.esta_afundado():
                for pos in navio.posicoes:
                    if not tabuleiro_adversario.foi_atacada(pos):
                        alvos_garantidos.append(pos)
        if alvos_garantidos:
            return self._rng.choice(alvos_garantidos)
        disponiveis = tabuleiro_adversario.posicoes_nao_atacadas()
        if disponiveis:
            return self._rng.choice(disponiveis)
        raise ValueError('Não há mais coordenadas disponíveis para ataque.')

    def reposicionar_frota_propria(self, tabuleiro_proprio: Tabuleiro) -> None:
        navios_intocados = [navio for navio in tabuleiro_proprio.navios if len(navio.posicoes_atingidas) == 0]
        if not navios_intocados:
            return
        for navio in navios_intocados:
            tabuleiro_proprio.remover_navio(navio)
        for navio in navios_intocados:
            posicionado = False
            tentativas = 0
            while not posicionado and tentativas < 500:
                tentativas += 1
                orientacao = self._rng.choice([Orientacao.HORIZONTAL, Orientacao.VERTICAL])
                if orientacao == Orientacao.HORIZONTAL:
                    max_l = tabuleiro_proprio.tamanho - 1
                    max_c = tabuleiro_proprio.tamanho - navio.tamanho
                else:
                    max_l = tabuleiro_proprio.tamanho - navio.tamanho
                    max_c = tabuleiro_proprio.tamanho - 1
                l = self._rng.randint(0, max_l)
                c = self._rng.randint(0, max_c)
                pos = Posicao(l, c)
                if tabuleiro_proprio.pode_posicionar(navio.tipo, pos, orientacao):
                    temp_navio = Navio(navio.tipo, pos, orientacao, sprite_id=navio.sprite_id)
                    conflito_tiro = any((tabuleiro_proprio.foi_atacada(p) for p in temp_navio.posicoes))
                    if not conflito_tiro:
                        tabuleiro_proprio.adicionar_navio(temp_navio)
                        posicionado = True
            if not posicionado:
                tabuleiro_proprio.adicionar_navio(navio)
