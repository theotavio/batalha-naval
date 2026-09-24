from __future__ import annotations
import random
from typing import Any
from backend.constantes import ResultadoTiro, EstadoCelula, TAMANHO_TABULEIRO, FROTA_PADRAO
from backend.ia.ia_base import IABase
from backend.models.posicao import Posicao
from backend.models.tabuleiro import Tabuleiro

class IADificil(IABase):

    def __init__(self, seed: int | None=None) -> None:
        self._rng = random.Random(seed)
        self.navios_afundados: list[Any] = []

    def reiniciar(self) -> None:
        self.navios_afundados.clear()

    def registrar_resultado(self, posicao: Posicao, resultado: ResultadoTiro, navio_afundado: Any | None) -> None:
        if resultado == ResultadoTiro.AFUNDADO and navio_afundado is not None:
            self.navios_afundados.append(navio_afundado)

    def _obter_tamanhos_navios_restantes(self, tabuleiro: Tabuleiro) -> list[int]:
        tamanhos = [tipo.tamanho for tipo in FROTA_PADRAO]
        for navio in self.navios_afundados:
            tam = getattr(navio, 'tamanho', None)
            if tam is None and hasattr(navio, 'posicoes'):
                tam = len(navio.posicoes)
            if tam is None:
                tam = 2
            if tam in tamanhos:
                tamanhos.remove(tam)
        return tamanhos if tamanhos else [2]

    def calcular_matriz_probabilidade(self, tabuleiro: Tabuleiro) -> list[list[float]]:
        tamanhos_restantes = self._obter_tamanhos_navios_restantes(tabuleiro)
        menor_tamanho = min(tamanhos_restantes)
        matriz = [[0.0 for _ in range(TAMANHO_TABULEIRO)] for _ in range(TAMANHO_TABULEIRO)]
        acertos_vivos: set[tuple[int, int]] = set()
        for l in range(TAMANHO_TABULEIRO):
            for c in range(TAMANHO_TABULEIRO):
                if tabuleiro.obter_celula(l, c) == EstadoCelula.ACERTO:
                    acertos_vivos.add((l, c))
        tem_acertos = len(acertos_vivos) > 0
        for tamanho in tamanhos_restantes:
            for l in range(TAMANHO_TABULEIRO):
                for c in range(TAMANHO_TABULEIRO - tamanho + 1):
                    segmento = [(l, c + i) for i in range(tamanho)]
                    valido = True
                    acertos_no_seg = 0
                    nao_atacadas: list[tuple[int, int]] = []
                    for pl, pc in segmento:
                        pos = Posicao(pl, pc)
                        if tabuleiro.foi_atacada(pos):
                            cel = tabuleiro.obter_celula(pl, pc)
                            if cel in (EstadoCelula.AGUA, EstadoCelula.AFUNDADO):
                                valido = False
                                break
                            elif cel == EstadoCelula.ACERTO:
                                acertos_no_seg += 1
                        else:
                            nao_atacadas.append((pl, pc))
                    if valido and nao_atacadas:
                        if tem_acertos:
                            if acertos_no_seg > 0:
                                peso = 1000.0 * (50.0 ** acertos_no_seg)
                            else:
                                peso = 0.01
                        else:
                            peso = 1.0
                            if menor_tamanho >= 2:
                                for pl, pc in nao_atacadas:
                                    if (pl + pc) % menor_tamanho == 0:
                                        peso += 0.8
                        for pl, pc in nao_atacadas:
                            matriz[pl][pc] += peso
            for l in range(TAMANHO_TABULEIRO - tamanho + 1):
                for c in range(TAMANHO_TABULEIRO):
                    segmento = [(l + i, c) for i in range(tamanho)]
                    valido = True
                    acertos_no_seg = 0
                    nao_atacadas = []
                    for pl, pc in segmento:
                        pos = Posicao(pl, pc)
                        if tabuleiro.foi_atacada(pos):
                            cel = tabuleiro.obter_celula(pl, pc)
                            if cel in (EstadoCelula.AGUA, EstadoCelula.AFUNDADO):
                                valido = False
                                break
                            elif cel == EstadoCelula.ACERTO:
                                acertos_no_seg += 1
                        else:
                            nao_atacadas.append((pl, pc))
                    if valido and nao_atacadas:
                        if tem_acertos:
                            if acertos_no_seg > 0:
                                peso = 1000.0 * (50.0 ** acertos_no_seg)
                            else:
                                peso = 0.01
                        else:
                            peso = 1.0
                            if menor_tamanho >= 2:
                                for pl, pc in nao_atacadas:
                                    if (pl + pc) % menor_tamanho == 0:
                                        peso += 0.8
                        for pl, pc in nao_atacadas:
                            matriz[pl][pc] += peso
        return matriz

    def escolher_jogada(self, tabuleiro_adversario: Tabuleiro) -> Posicao:
        matriz = self.calcular_matriz_probabilidade(tabuleiro_adversario)
        maior_prob = -1.0
        melhores_posicoes: list[Posicao] = []
        for l in range(TAMANHO_TABULEIRO):
            for c in range(TAMANHO_TABULEIRO):
                pos = Posicao(l, c)
                if not tabuleiro_adversario.foi_atacada(pos):
                    prob = matriz[l][c]
                    if prob > maior_prob:
                        maior_prob = prob
                        melhores_posicoes = [pos]
                    elif abs(prob - maior_prob) < 1e-06:
                        melhores_posicoes.append(pos)
        if not melhores_posicoes or maior_prob <= 0.0:
            disponiveis = tabuleiro_adversario.posicoes_nao_atacadas()
            return self._rng.choice(disponiveis)
        return self._rng.choice(melhores_posicoes)
