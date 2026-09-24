from __future__ import annotations
import math
from typing import Callable, Any
import pygame
from backend.constantes import ResultadoTiro
from frontend.core.gerenciador_som import GerenciadorSom
from frontend.animacoes.particulas import SistemaParticulas

class AnimacaoTiro:

    def __init__(self, origem: tuple[float, float], destino: tuple[float, float], resultado: ResultadoTiro, sistema_particulas: SistemaParticulas, on_impacto: Callable[[], Any] | None=None, duracao: float=0.45) -> None:
        self.origem = origem
        self.destino = destino
        self.resultado = resultado
        self.sistema_particulas = sistema_particulas
        self.on_impacto = on_impacto
        self.duracao = duracao
        self.tempo_decorrido: float = 0.0
        self.finalizada: bool = False
        self._impacto_executado: bool = False
        GerenciadorSom.obter_instancia().tocar_som('cannon_fire')

    def atualizar(self, dt: float) -> None:
        if self.finalizada:
            return
        self.tempo_decorrido += dt
        t = min(1.0, self.tempo_decorrido / self.duracao)
        x = self.origem[0] + (self.destino[0] - self.origem[0]) * t
        y = self.origem[1] + (self.destino[1] - self.origem[1]) * t
        altura_arco = 70.0 * math.sin(t * math.pi)
        y -= altura_arco
        self.sistema_particulas.emitir_fumaca_continua(x, y)
        if t >= 1.0 and (not self._impacto_executado):
            self._executar_impacto()

    def _executar_impacto(self) -> None:
        self._impacto_executado = True
        self.finalizada = True
        som = GerenciadorSom.obter_instancia()
        dest_x, dest_y = self.destino
        if self.resultado == ResultadoTiro.AFUNDADO:
            self.sistema_particulas.emitir_explosao(dest_x, dest_y, quantidade=50)
            som.tocar_som('ship_destroyed')
        elif self.resultado == ResultadoTiro.ACERTO:
            self.sistema_particulas.emitir_explosao(dest_x, dest_y, quantidade=30)
            som.tocar_som('cannon_hit')
        else:
            self.sistema_particulas.emitir_agua_splash(dest_x, dest_y, quantidade=30)
            som.tocar_som('cannon_miss')
        if self.on_impacto:
            self.on_impacto()

    def desenhar(self, superficie: pygame.Surface) -> None:
        if self.finalizada:
            return
        t = min(1.0, self.tempo_decorrido / self.duracao)
        x = self.origem[0] + (self.destino[0] - self.origem[0]) * t
        y = self.origem[1] + (self.destino[1] - self.origem[1]) * t - 70.0 * math.sin(t * math.pi)
        pygame.draw.circle(superficie, (40, 40, 40), (int(x), int(y)), 6)
        pygame.draw.circle(superficie, (200, 200, 200), (int(x - 2), int(y - 2)), 2)
