from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any
from backend.constantes import ResultadoTiro
from backend.models.posicao import Posicao
if TYPE_CHECKING:
    from backend.models.tabuleiro import Tabuleiro

class IABase(ABC):

    @abstractmethod
    def escolher_jogada(self, tabuleiro_adversario: Tabuleiro) -> Posicao:
        pass

    @abstractmethod
    def registrar_resultado(self, posicao: Posicao, resultado: ResultadoTiro, navio_afundado: Any | None) -> None:
        pass

    @abstractmethod
    def reiniciar(self) -> None:
        pass
