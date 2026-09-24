from __future__ import annotations
from typing import Any
from backend.constantes import TipoNavio, Orientacao, TAMANHO_TABULEIRO
from backend.excecoes import NavioForaDoTabuleiroErro
from backend.models.posicao import Posicao

class Navio:

    def __init__(self, tipo: TipoNavio, posicao_inicial: Posicao, orientacao: Orientacao=Orientacao.HORIZONTAL, sprite_id: int | None=None) -> None:
        self.tipo = tipo
        self.posicao_inicial = posicao_inicial
        self.orientacao = orientacao
        self.sprite_id = sprite_id
        self.posicoes = self._calcular_posicoes()
        self.posicoes_atingidas: set[Posicao] = set()

    @property
    def tamanho(self) -> int:
        return self.tipo.tamanho

    def _calcular_posicoes(self) -> list[Posicao]:
        posicoes: list[Posicao] = []
        linha_base = self.posicao_inicial.linha
        coluna_base = self.posicao_inicial.coluna
        for i in range(self.tamanho):
            if self.orientacao == Orientacao.HORIZONTAL:
                l = linha_base
                c = coluna_base + i
            else:
                l = linha_base + i
                c = coluna_base
            pos = Posicao.criar_segura(l, c)
            if pos is None:
                raise NavioForaDoTabuleiroErro(f'Navio {self.tipo.value} na posição {self.posicao_inicial} e orientação {self.orientacao.value} excede os limites do tabuleiro.')
            posicoes.append(pos)
        return posicoes

    def contem_posicao(self, posicao: Posicao) -> bool:
        return posicao in self.posicoes

    def atingir(self, posicao: Posicao) -> bool:
        if self.contem_posicao(posicao):
            self.posicoes_atingidas.add(posicao)
            return True
        return False

    def esta_afundado(self) -> bool:
        return len(self.posicoes_atingidas) == len(self.posicoes)

    def sobrepoe(self, outro: Navio) -> bool:
        return bool(set(self.posicoes).intersection(set(outro.posicoes)))

    def para_dict(self) -> dict[str, Any]:
        return {'tipo': self.tipo.value, 'linha_inicial': self.posicao_inicial.linha, 'coluna_inicial': self.posicao_inicial.coluna, 'orientacao': self.orientacao.value, 'sprite_id': self.sprite_id, 'posicoes_atingidas': [(p.linha, p.coluna) for p in self.posicoes_atingidas]}

    @classmethod
    def de_dict(cls, data: dict[str, Any]) -> Navio:
        tipo = TipoNavio(data['tipo'])
        posicao_inicial = Posicao(linha=data['linha_inicial'], coluna=data['coluna_inicial'])
        orientacao = Orientacao(data['orientacao'])
        sprite_id = data.get('sprite_id')
        navio = cls(tipo=tipo, posicao_inicial=posicao_inicial, orientacao=orientacao, sprite_id=sprite_id)
        for linha, coluna in data.get('posicoes_atingidas', []):
            navio.posicoes_atingidas.add(Posicao(linha=linha, coluna=coluna))
        return navio

    def __repr__(self) -> str:
        return f'Navio({self.tipo.value}, inicio={self.posicao_inicial}, orientacao={self.orientacao.value}, afundado={self.esta_afundado()})'
