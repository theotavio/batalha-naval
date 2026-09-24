from __future__ import annotations
import math
import time
from typing import Callable, Any
import pygame
from backend.constantes import TAMANHO_TABULEIRO, LETRAS_COLUNAS, NUMEROS_LINHAS, EstadoCelula, TipoNavio, Orientacao
from backend.models.posicao import Posicao
from backend.models.tabuleiro import Tabuleiro
from backend.models.navio import Navio
from frontend.core.constantes import TAMANHO_CELULA, MARGEM_COORDENADAS, COR_PAINEL, COR_PAINEL_BORDA, COR_AGUA_GRID, COR_AGUA_GRID_HOVER, COR_LINHA_GRID, COR_CELULA_ACERTO, COR_CELULA_AFUNDADO, COR_CELULA_AGUA, COR_TEXTO_BRANCO, COR_TEXTO_MUTED, COR_TEXTO_DOURADO, COR_SUCESSO, COR_PERIGO
from frontend.core.gerenciador_assets import GerenciadorAssets

class TabuleiroRender:

    def __init__(self, x: int, y: int, tabuleiro: Tabuleiro, titulo: str='TABULEIRO', revelar_navios: bool=True, interativo: bool=True, on_celula_clicada: Callable[[Posicao], Any] | None=None, celula_tamanho: int=TAMANHO_CELULA) -> None:
        self.x = x
        self.y = y
        self.tabuleiro = tabuleiro
        self.titulo = titulo
        self.revelar_navios = revelar_navios
        self.interativo = interativo
        self.on_celula_clicada = on_celula_clicada
        self.celula_tamanho = celula_tamanho
        self.largura_grid = self.celula_tamanho * TAMANHO_TABULEIRO
        self.altura_grid = self.celula_tamanho * TAMANHO_TABULEIRO
        self.grid_x = self.x + MARGEM_COORDENADAS
        self.grid_y = self.y + MARGEM_COORDENADAS + 20
        self.celula_hover: Posicao | None = None
        self.navio_fantasma: tuple[TipoNavio, Orientacao] | None = None
        self.fantasma_valido: bool = True

    def obter_posicao_celula_mouse(self, mouse_pos: tuple[int, int]) -> Posicao | None:
        mx, my = mouse_pos
        rel_x = mx - self.grid_x
        rel_y = my - self.grid_y
        if 0 <= rel_x < self.largura_grid and 0 <= rel_y < self.altura_grid:
            coluna = rel_x // self.celula_tamanho
            linha = rel_y // self.celula_tamanho
            return Posicao.criar_segura(linha, coluna)
        return None

    def obter_pixel_celula(self, linha: int, coluna: int) -> tuple[int, int]:
        cx = self.grid_x + coluna * self.celula_tamanho + self.celula_tamanho // 2
        cy = self.grid_y + linha * self.celula_tamanho + self.celula_tamanho // 2
        return (cx, cy)

    def processar_evento(self, evento: pygame.event.Event) -> bool:
        if not self.interativo:
            return False
        if evento.type == pygame.MOUSEMOTION:
            self.celula_hover = self.obter_posicao_celula_mouse(evento.pos)
            return self.celula_hover is not None
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = self.obter_posicao_celula_mouse(evento.pos)
            if pos and self.on_celula_clicada:
                self.on_celula_clicada(pos)
                return True
        return False

    def desenhar(self, superficie: pygame.Surface) -> None:
        assets = GerenciadorAssets.obter_instancia()
        fonte_tit = assets.obter_fonte('grande', negrito=True)
        fonte_coord = assets.obter_fonte('pequena', negrito=True)
        txt_tit = fonte_tit.render(self.titulo, True, COR_TEXTO_BRANCO)
        superficie.blit(txt_tit, (self.grid_x + (self.largura_grid - txt_tit.get_width()) // 2, self.y))
        painel_rect = pygame.Rect(self.grid_x - 4, self.grid_y - 4, self.largura_grid + 8, self.altura_grid + 8)
        pygame.draw.rect(superficie, COR_PAINEL, painel_rect, border_radius=8)
        pygame.draw.rect(superficie, COR_PAINEL_BORDA, painel_rect, width=2, border_radius=8)
        for c, letra in enumerate(LETRAS_COLUNAS):
            txt_letra = fonte_coord.render(letra, True, COR_TEXTO_DOURADO)
            lx = self.grid_x + c * self.celula_tamanho + (self.celula_tamanho - txt_letra.get_width()) // 2
            ly = self.grid_y - 20
            superficie.blit(txt_letra, (lx, ly))
        for l, num in enumerate(NUMEROS_LINHAS):
            txt_num = fonte_coord.render(str(num), True, COR_TEXTO_DOURADO)
            nx = self.grid_x - MARGEM_COORDENADAS + 6
            ny = self.grid_y + l * self.celula_tamanho + (self.celula_tamanho - txt_num.get_height()) // 2
            superficie.blit(txt_num, (nx, ny))
        for l in range(TAMANHO_TABULEIRO):
            for c in range(TAMANHO_TABULEIRO):
                cell_rect = pygame.Rect(self.grid_x + c * self.celula_tamanho, self.grid_y + l * self.celula_tamanho, self.celula_tamanho, self.celula_tamanho)
                cor_cell = COR_AGUA_GRID
                if self.interativo and self.celula_hover and (self.celula_hover.linha == l) and (self.celula_hover.coluna == c):
                    cor_cell = COR_AGUA_GRID_HOVER
                pygame.draw.rect(superficie, cor_cell, cell_rect)
                pygame.draw.rect(superficie, COR_LINHA_GRID, cell_rect, width=1)
        if self.revelar_navios:
            self._desenhar_navios(superficie, assets)
        if self.navio_fantasma and self.celula_hover:
            self._desenhar_fantasma(superficie)
        self._desenhar_marcadores_tiros(superficie, assets)

    def _desenhar_navios(self, superficie: pygame.Surface, assets: GerenciadorAssets) -> None:
        for navio in self.tabuleiro.navios:
            l_ini = navio.posicao_inicial.linha
            c_ini = navio.posicao_inicial.coluna
            px = self.grid_x + c_ini * self.celula_tamanho
            py = self.grid_y + l_ini * self.celula_tamanho
            surf_navio = assets.obter_navio_surface(navio.tamanho, navio.orientacao.value, celula_px=self.celula_tamanho, sprite_id=navio.sprite_id, afundado=navio.esta_afundado())
            superficie.blit(surf_navio, (px, py))

    def _desenhar_fantasma(self, superficie: pygame.Surface) -> None:
        if not self.navio_fantasma or not self.celula_hover:
            return
        tipo, orientacao = self.navio_fantasma
        tamanho = tipo.tamanho
        linha_base = self.celula_hover.linha
        coluna_base = self.celula_hover.coluna
        valido = self.tabuleiro.pode_posicionar(tipo, self.celula_hover, orientacao)
        cor_fantasma = (*COR_SUCESSO, 140) if valido else (*COR_PERIGO, 140)
        for i in range(tamanho):
            l = linha_base if orientacao == Orientacao.HORIZONTAL else linha_base + i
            c = coluna_base + i if orientacao == Orientacao.HORIZONTAL else coluna_base
            if 0 <= l < TAMANHO_TABULEIRO and 0 <= c < TAMANHO_TABULEIRO:
                rect = pygame.Rect(self.grid_x + c * self.celula_tamanho, self.grid_y + l * self.celula_tamanho, self.celula_tamanho, self.celula_tamanho)
                surf = pygame.Surface((self.celula_tamanho, self.celula_tamanho), pygame.SRCALPHA)
                surf.fill(cor_fantasma)
                superficie.blit(surf, rect)
                pygame.draw.rect(superficie, (255, 255, 255), rect, width=2)

    def _desenhar_marcadores_tiros(self, superficie: pygame.Surface, assets: GerenciadorAssets) -> None:
        for l in range(TAMANHO_TABULEIRO):
            for c in range(TAMANHO_TABULEIRO):
                estado = self.tabuleiro.obter_celula(l, c)
                if estado == EstadoCelula.VAZIO or estado == EstadoCelula.NAVIO:
                    continue
                cx, cy = self.obter_pixel_celula(l, c)
                if estado == EstadoCelula.AGUA:
                    pygame.draw.circle(superficie, COR_TEXTO_MUTED, (cx, cy), 6)
                    pygame.draw.circle(superficie, (255, 255, 255), (cx, cy), 3)
                elif estado == EstadoCelula.ACERTO:
                    sprite_fogo = assets.obter_sprite('fire1.png')
                    if sprite_fogo:
                        fogo_redim = pygame.transform.smoothscale(sprite_fogo, (24, 24))
                        superficie.blit(fogo_redim, (cx - 12, cy - 12))
                    else:
                        pygame.draw.circle(superficie, COR_CELULA_ACERTO, (cx, cy), 10)
                        pygame.draw.circle(superficie, (255, 200, 0), (cx, cy), 5)
                elif estado == EstadoCelula.AFUNDADO:
                    pygame.draw.circle(superficie, COR_CELULA_AFUNDADO, (cx, cy), 12)
                    d = 7
                    pygame.draw.line(superficie, (255, 255, 255), (cx - d, cy - d), (cx + d, cy + d), 3)
                    pygame.draw.line(superficie, (255, 255, 255), (cx - d, cy + d), (cx + d, cy - d), 3)
