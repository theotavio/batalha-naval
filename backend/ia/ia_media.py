from __future__ import annotations
import random
from typing import Any
from backend.constantes import ResultadoTiro, EstadoCelula
from backend.ia.ia_base import IABase
from backend.models.posicao import Posicao
from backend.models.tabuleiro import Tabuleiro

class IAMedia(IABase):

    def __init__(self, seed: int | None=None) -> None:
        self._rng = random.Random(seed)
        self.fila_alvos: list[Posicao] = []
        self.acertos_atuais: list[Posicao] = []
        self.acertos_pendentes_globais: list[Posicao] = []

    def reiniciar(self) -> None:
        self.fila_alvos.clear()
        self.acertos_atuais.clear()
        self.acertos_pendentes_globais.clear()

    def escolher_jogada(self, tabuleiro_adversario: Tabuleiro) -> Posicao:
        self.fila_alvos = [p for p in self.fila_alvos if not tabuleiro_adversario.foi_atacada(p)]
        if self.fila_alvos:
            return self.fila_alvos.pop(0)
        if self.acertos_pendentes_globais:
            ponto = self.acertos_pendentes_globais.pop(0)
            self._adicionar_vizinhos_ao_alvo(ponto, tabuleiro_adversario)
            if self.fila_alvos:
                return self.fila_alvos.pop(0)
        disponiveis = tabuleiro_adversario.posicoes_nao_atacadas()
        if not disponiveis:
            raise ValueError('Nenhuma posição disponível.')
        paritarias = [p for p in disponiveis if (p.linha + p.coluna) % 2 == 0]
        if paritarias:
            return self._rng.choice(paritarias)
        return self._rng.choice(disponiveis)

    def _adicionar_vizinhos_ao_alvo(self, ponto: Posicao, tabuleiro: Tabuleiro) -> None:
        for viz in ponto.obter_vizinhas_ortogonais():
            if not tabuleiro.foi_atacada(viz) and viz not in self.fila_alvos:
                self.fila_alvos.append(viz)

    def registrar_resultado(self, posicao: Posicao, resultado: ResultadoTiro, navio_afundado: Any | None) -> None:
        if resultado == ResultadoTiro.ACERTO:
            self.acertos_atuais.append(posicao)
            self.acertos_pendentes_globais.append(posicao)
            if len(self.acertos_atuais) == 1:
                for viz in posicao.obter_vizinhas_ortogonais():
                    if viz not in self.fila_alvos:
                        self.fila_alvos.append(viz)
            else:
                linhas = [p.linha for p in self.acertos_atuais]
                colunas = [p.coluna for p in self.acertos_atuais]
                if len(set(linhas)) == 1:
                    l = linhas[0]
                    min_c = min(colunas)
                    max_c = max(colunas)
                    self.fila_alvos = [p for p in self.fila_alvos if p.linha == l]
                    pos_esq = Posicao.criar_segura(l, min_c - 1)
                    pos_dir = Posicao.criar_segura(l, max_c + 1)
                    if pos_esq and pos_esq not in self.fila_alvos:
                        self.fila_alvos.insert(0, pos_esq)
                    if pos_dir and pos_dir not in self.fila_alvos:
                        self.fila_alvos.append(pos_dir)
                elif len(set(colunas)) == 1:
                    c = colunas[0]
                    min_l = min(linhas)
                    max_l = max(linhas)
                    self.fila_alvos = [p for p in self.fila_alvos if p.coluna == c]
                    pos_cima = Posicao.criar_segura(min_l - 1, c)
                    pos_baixo = Posicao.criar_segura(max_l + 1, c)
                    if pos_cima and pos_cima not in self.fila_alvos:
                        self.fila_alvos.insert(0, pos_cima)
                    if pos_baixo and pos_baixo not in self.fila_alvos:
                        self.fila_alvos.append(pos_baixo)
        elif resultado == ResultadoTiro.AFUNDADO:
            if navio_afundado is not None and hasattr(navio_afundado, 'posicoes'):
                posicoes_navio = set(navio_afundado.posicoes)
                self.acertos_atuais = [p for p in self.acertos_atuais if p not in posicoes_navio]
                self.acertos_pendentes_globais = [p for p in self.acertos_pendentes_globais if p not in posicoes_navio]
                self.fila_alvos = [p for p in self.fila_alvos if p not in posicoes_navio]
            else:
                self.acertos_atuais.clear()
                self.fila_alvos.clear()
