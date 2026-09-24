from __future__ import annotations
from dataclasses import dataclass
import re
from backend.constantes import TAMANHO_TABULEIRO, LETRAS_COLUNAS, NUMEROS_LINHAS
from backend.excecoes import PosicaoInvalidaErro

@dataclass(frozen=True, order=True)
class Posicao:
    linha: int
    coluna: int

    def __post_init__(self) -> None:
        if not self.e_valida():
            raise PosicaoInvalidaErro(f'Posição ({self.linha}, {self.coluna}) fora dos limites do tabuleiro (0 a {TAMANHO_TABULEIRO - 1}).')

    def e_valida(self) -> bool:
        return 0 <= self.linha < TAMANHO_TABULEIRO and 0 <= self.coluna < TAMANHO_TABULEIRO

    def para_coordenada(self) -> str:
        letra = LETRAS_COLUNAS[self.coluna]
        numero = self.linha + 1
        return f'{letra}{numero}'

    @classmethod
    def de_coordenada(cls, coordenada: str) -> Posicao:
        if not coordenada or not isinstance(coordenada, str):
            raise PosicaoInvalidaErro('Coordenada não pode ser vazia.')
        texto = coordenada.strip().upper()
        match = re.match('^([A-J])([1-9]|10)$', texto)
        if not match:
            raise PosicaoInvalidaErro(f"Formato de coordenada '{coordenada}' inválido. Use formato Letra (A-J) e Número (1-10), ex: 'C5'.")
        letra_coluna, numero_linha = match.groups()
        coluna = LETRAS_COLUNAS.index(letra_coluna)
        linha = int(numero_linha) - 1
        return cls(linha=linha, coluna=coluna)

    @classmethod
    def criar_segura(cls, linha: int, coluna: int) -> Posicao | None:
        if 0 <= linha < TAMANHO_TABULEIRO and 0 <= coluna < TAMANHO_TABULEIRO:
            return cls(linha=linha, coluna=coluna)
        return None

    def obter_vizinhas_ortogonais(self) -> list[Posicao]:
        deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        vizinhas: list[Posicao] = []
        for dl, dc in deltas:
            pos = Posicao.criar_segura(self.linha + dl, self.coluna + dc)
            if pos:
                vizinhas.append(pos)
        return vizinhas

    def __str__(self) -> str:
        return self.para_coordenada()

    def __repr__(self) -> str:
        return f"Posicao({self.linha}, {self.coluna} -> '{self.para_coordenada()}')"
