from __future__ import annotations
import random
import pygame

class Particula:

    def __init__(self, x: float, y: float, vx: float, vy: float, cor: tuple[int, int, int], tamanho: float, vida_maxima: float, gravidade: float=0.0) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.cor = cor
        self.tamanho_inicial = tamanho
        self.tamanho = tamanho
        self.vida_maxima = vida_maxima
        self.vida = vida_maxima
        self.gravidade = gravidade

    def atualizar(self, dt: float) -> bool:
        self.vida -= dt
        if self.vida <= 0:
            return False
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.vy += self.gravidade * dt * 60
        progresso = max(0.0, self.vida / self.vida_maxima)
        self.tamanho = self.tamanho_inicial * progresso
        return True

    def desenhar(self, superficie: pygame.Surface) -> None:
        if self.tamanho <= 0.5:
            return
        progresso = max(0.0, min(1.0, self.vida / self.vida_maxima))
        alpha = int(255 * progresso)
        surf = pygame.Surface((int(self.tamanho * 2), int(self.tamanho * 2)), pygame.SRCALPHA)
        cor_com_alpha = (*self.cor, alpha)
        pygame.draw.circle(surf, cor_com_alpha, (int(self.tamanho), int(self.tamanho)), int(self.tamanho))
        superficie.blit(surf, (self.x - self.tamanho, self.y - self.tamanho))

class SistemaParticulas:

    def __init__(self) -> None:
        self.particulas: list[Particula] = []

    def limpar(self) -> None:
        self.particulas.clear()

    def emitir_explosao(self, x: float, y: float, quantidade: int=35) -> None:
        cores = [(255, 69, 0), (255, 140, 0), (255, 215, 0), (220, 38, 38), (255, 255, 255)]
        for _ in range(quantidade):
            ang = random.uniform(0, 6.28)
            vel = random.uniform(1.5, 5.5)
            vx = vel * random.uniform(0.5, 1.2) * (1 if random.random() > 0.5 else -1)
            vy = vel * random.uniform(0.5, 1.2) * (1 if random.random() > 0.5 else -1)
            cor = random.choice(cores)
            tamanho = random.uniform(3.0, 7.0)
            vida = random.uniform(0.4, 0.9)
            self.particulas.append(Particula(x, y, vx, vy, cor, tamanho, vida, gravidade=0.05))

    def emitir_agua_splash(self, x: float, y: float, quantidade: int=25) -> None:
        cores = [(56, 189, 248), (96, 165, 250), (224, 242, 254), (14, 165, 233)]
        for _ in range(quantidade):
            vx = random.uniform(-2.5, 2.5)
            vy = random.uniform(-4.5, -1.0)
            cor = random.choice(cores)
            tamanho = random.uniform(2.5, 5.5)
            vida = random.uniform(0.4, 0.7)
            self.particulas.append(Particula(x, y, vx, vy, cor, tamanho, vida, gravidade=0.15))

    def emitir_fumaca_continua(self, x: float, y: float) -> None:
        cores = [(100, 116, 139), (71, 85, 105), (148, 163, 184)]
        if random.random() < 0.3:
            vx = random.uniform(-0.5, 0.5)
            vy = random.uniform(-1.2, -0.4)
            cor = random.choice(cores)
            tamanho = random.uniform(3.0, 6.0)
            vida = random.uniform(0.6, 1.1)
            self.particulas.append(Particula(x, y, vx, vy, cor, tamanho, vida, gravidade=-0.02))

    def atualizar(self, dt: float) -> None:
        self.particulas = [p for p in self.particulas if p.atualizar(dt)]

    def desenhar(self, superficie: pygame.Surface) -> None:
        for p in self.particulas:
            p.desenhar(superficie)
