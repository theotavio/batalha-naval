from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any
import pygame
if TYPE_CHECKING:
    from main import JogoPrincipal

class TelaBase(ABC):

    def __init__(self, jogo: JogoPrincipal) -> None:
        self.jogo = jogo

    def inicializar(self, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def processar_evento(self, evento: pygame.event.Event) -> None:
        pass

    @abstractmethod
    def atualizar(self, dt: float) -> None:
        pass

    @abstractmethod
    def desenhar(self, superficie: pygame.Surface) -> None:
        pass
