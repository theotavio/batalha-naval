from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any
from backend.constantes import ResultadoTiro
from backend.models.tabuleiro import Tabuleiro
from backend.models.posicao import Posicao
if TYPE_CHECKING:
    from backend.ia.ia_base import IABase

class Jogador(ABC):

    def __init__(self, nome: str, id_jogador: int | str=0) -> None:
        self.id_jogador = id_jogador
        self.nome = nome
        self.tabuleiro = Tabuleiro()
        self.total_tiros: int = 0
        self.total_acertos: int = 0
        self.maior_sequencia_acertos: int = 0
        self.sequencia_atual_acertos: int = 0

    @property
    def total_erros(self) -> int:
        return self.total_tiros - self.total_acertos

    @property
    def aproveitamento(self) -> float:
        if self.total_tiros == 0:
            return 0.0
        return self.total_acertos / self.total_tiros * 100.0

    def registrar_resultado_tiro(self, resultado: ResultadoTiro) -> None:
        self.total_tiros += 1
        if resultado in (ResultadoTiro.ACERTO, ResultadoTiro.AFUNDADO):
            self.total_acertos += 1
            self.sequencia_atual_acertos += 1
            if self.sequencia_atual_acertos > self.maior_sequencia_acertos:
                self.maior_sequencia_acertos = self.sequencia_atual_acertos
        else:
            self.sequencia_atual_acertos = 0

    @abstractmethod
    def e_humano(self) -> bool:
        pass

    def __repr__(self) -> str:
        return f"Jogador(nome='{self.nome}', id={self.id_jogador})"

class JogadorHumano(Jogador):

    def e_humano(self) -> bool:
        return True

class JogadorComputador(Jogador):

    def __init__(self, nome: str='Computador', ia: IABase | None=None, id_jogador: int | str=0) -> None:
        super().__init__(nome=nome, id_jogador=id_jogador)
        self.ia = ia

    def e_humano(self) -> bool:
        return False

    def escolher_jogada(self, tabuleiro_adversario: Tabuleiro) -> Posicao:
        if self.ia is None:
            candidatos = tabuleiro_adversario.posicoes_nao_atacadas()
            import random
            return random.choice(candidatos)
        return self.ia.escolher_jogada(tabuleiro_adversario)

    def registrar_feedback_ia(self, posicao: Posicao, resultado: ResultadoTiro, navio_afundado: Any | None) -> None:
        if self.ia is not None:
            self.ia.registrar_resultado(posicao, resultado, navio_afundado)

class JogadorRemoto(Jogador):

    def __init__(self, nome: str, id_jogador: int | str=0) -> None:
        super().__init__(nome=nome, id_jogador=id_jogador)

    def e_humano(self) -> bool:
        return False
