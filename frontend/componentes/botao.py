from __future__ import annotations
from typing import Callable, Any
import pygame
from frontend.core.constantes import COR_PRIMARIA, COR_PRIMARIA_HOVER, COR_PAINEL, COR_PAINEL_BORDA, COR_TEXTO_BRANCO, COR_TEXTO_MUTED
from frontend.core.gerenciador_assets import GerenciadorAssets
from frontend.core.gerenciador_som import GerenciadorSom

class Botao:

    def __init__(self, rect: tuple[int, int, int, int] | pygame.Rect, texto: str, on_click: Callable[[], Any] | None=None, cor_base: tuple[int, int, int]=COR_PRIMARIA, cor_hover: tuple[int, int, int]=COR_PRIMARIA_HOVER, cor_texto: tuple[int, int, int]=COR_TEXTO_BRANCO, tamanho_fonte: str='media', icone: pygame.Surface | None=None, arredondamento: int=8, ativo: bool=True, som_click: str='SoundMenuAccept') -> None:
        self.rect = pygame.Rect(rect)
        self.texto = texto
        self.on_click = on_click
        self.cor_base = cor_base
        self.cor_hover = cor_hover
        self.cor_texto = cor_texto
        self.tamanho_fonte = tamanho_fonte
        self.icone = icone
        self.arredondamento = arredondamento
        self.ativo = ativo
        self.som_click = som_click
        self.hover: bool = False
        self.pressionado: bool = False
        self._hover_anterior: bool = False

    def processar_evento(self, evento: pygame.event.Event) -> bool:
        if not self.ativo:
            return False
        if evento.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(evento.pos)
            if self.hover and (not self._hover_anterior):
                GerenciadorSom.obter_instancia().tocar_som('SoundMenuMove')
            self._hover_anterior = self.hover
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                self.pressionado = True
        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            if self.pressionado and self.rect.collidepoint(evento.pos):
                self.pressionado = False
                GerenciadorSom.obter_instancia().tocar_som(self.som_click)
                if self.on_click:
                    self.on_click()
                return True
            self.pressionado = False
        return False

    def desenhar(self, superficie: pygame.Surface) -> None:
        assets = GerenciadorAssets.obter_instancia()
        largura_maxima = self.rect.width - 24
        if self.icone:
            largura_maxima -= self.icone.get_width() + 10
        tamanhos_tentativa = [self.tamanho_fonte]
        if self.tamanho_fonte == 'destaque':
            tamanhos_tentativa.extend(['titulo', 'grande', 'media', 'pequena'])
        elif self.tamanho_fonte == 'titulo':
            tamanhos_tentativa.extend(['grande', 'media', 'pequena'])
        elif self.tamanho_fonte == 'grande':
            tamanhos_tentativa.extend(['media', 'pequena'])
        elif self.tamanho_fonte == 'media':
            tamanhos_tentativa.append('pequena')
        fonte_escolhida = assets.obter_fonte(self.tamanho_fonte, negrito=True)
        for tam in tamanhos_tentativa:
            f = assets.obter_fonte(tam, negrito=True)
            if f.size(self.texto)[0] <= largura_maxima:
                fonte_escolhida = f
                break
        cor_bg = self.cor_hover if self.hover and self.ativo else self.cor_base
        if not self.ativo:
            cor_bg = (55, 65, 80)
        sombra_rect = self.rect.copy()
        sombra_rect.y += 3
        sombra_surf = pygame.Surface((sombra_rect.width, sombra_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(sombra_surf, (0, 0, 0, 80), sombra_surf.get_rect(), border_radius=self.arredondamento)
        superficie.blit(sombra_surf, sombra_rect)
        btn_rect = self.rect.copy()
        if self.pressionado and self.ativo:
            btn_rect.y += 2
        pygame.draw.rect(superficie, cor_bg, btn_rect, border_radius=self.arredondamento)
        cor_borda = (255, 255, 255, 140) if self.hover and self.ativo else (255, 255, 255, 40)
        pygame.draw.rect(superficie, cor_borda, btn_rect, width=2 if self.hover and self.ativo else 1, border_radius=self.arredondamento)
        cor_txt = self.cor_texto if self.ativo else COR_TEXTO_MUTED
        txt_surf = fonte_escolhida.render(self.texto, True, cor_txt)
        txt_rect = txt_surf.get_rect(center=btn_rect.center)
        if self.icone:
            espaco = 8
            largura_total = self.icone.get_width() + espaco + txt_surf.get_width()
            inicio_x = btn_rect.centerx - largura_total // 2
            icone_y = btn_rect.centery - self.icone.get_height() // 2
            superficie.blit(self.icone, (inicio_x, icone_y))
            superficie.blit(txt_surf, (inicio_x + self.icone.get_width() + espaco, txt_rect.y))
        else:
            superficie.blit(txt_surf, txt_rect)
