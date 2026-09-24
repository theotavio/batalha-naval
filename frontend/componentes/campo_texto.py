from __future__ import annotations
import time
from typing import Callable, Any
import pygame
from frontend.core.constantes import COR_PAINEL, COR_PAINEL_BORDA, COR_PAINEL_GLOW, COR_TEXTO_BRANCO, COR_TEXTO_MUTED
from frontend.core.gerenciador_assets import GerenciadorAssets
from frontend.core.gerenciador_som import GerenciadorSom

class CampoTexto:

    def __init__(self, rect: tuple[int, int, int, int] | pygame.Rect, texto_inicial: str='', placeholder: str='Digite seu nome...', max_caracteres: int=18, on_submit: Callable[[str], Any] | None=None) -> None:
        self.rect = pygame.Rect(rect)
        self.texto = texto_inicial
        self.placeholder = placeholder
        self.max_caracteres = max_caracteres
        self.on_submit = on_submit
        self.focado: bool = False
        self._tempo_cursor: float = 0.0
        self._cursor_visivel: bool = True

    def processar_evento(self, evento: pygame.event.Event) -> bool:
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            self.focado = self.rect.collidepoint(evento.pos)
            return self.focado
        elif evento.type == pygame.KEYDOWN and self.focado:
            mods = pygame.key.get_mods()
            if (mods & pygame.KMOD_CTRL or mods & pygame.KMOD_META) and evento.key == pygame.K_v:
                try:
                    if not pygame.scrap.get_init():
                        pygame.scrap.init()
                    conteudo = pygame.scrap.get(pygame.SCRAP_TEXT)
                    if conteudo:
                        texto_colado = conteudo.decode('utf-8', errors='ignore').rstrip('\x00\r\n ')
                        espaco_restante = self.max_caracteres - len(self.texto)
                        if espaco_restante > 0:
                            self.texto += texto_colado[:espaco_restante]
                            GerenciadorSom.obter_instancia().tocar_som('SoundBeep')
                        return True
                except Exception:
                    pass
            elif (mods & pygame.KMOD_CTRL or mods & pygame.KMOD_META) and evento.key == pygame.K_a:
                self.texto = ''
                return True
            elif evento.key == pygame.K_RETURN or evento.key == pygame.K_KP_ENTER:
                GerenciadorSom.obter_instancia().tocar_som('SoundMenuAccept')
                if self.on_submit:
                    self.on_submit(self.texto.strip())
                return True
            elif evento.key == pygame.K_BACKSPACE:
                self.texto = self.texto[:-1]
                GerenciadorSom.obter_instancia().tocar_som('SoundBeep')
            elif evento.key == pygame.K_ESCAPE:
                self.focado = False
            elif len(self.texto) < self.max_caracteres and evento.unicode.isprintable():
                self.texto += evento.unicode
                GerenciadorSom.obter_instancia().tocar_som('SoundBeep')
        return False

    def atualizar(self, dt: float) -> None:
        if self.focado:
            self._tempo_cursor += dt
            if self._tempo_cursor >= 0.5:
                self._cursor_visivel = not self._cursor_visivel
                self._tempo_cursor = 0.0
        else:
            self._cursor_visivel = False

    def desenhar(self, superficie: pygame.Surface) -> None:
        assets = GerenciadorAssets.obter_instancia()
        fonte = assets.obter_fonte('grande')
        if fonte.size(self.texto or self.placeholder)[0] > self.rect.width - 32:
            fonte = assets.obter_fonte('media')
        if fonte.size(self.texto or self.placeholder)[0] > self.rect.width - 32:
            fonte = assets.obter_fonte('pequena')
        pygame.draw.rect(superficie, COR_PAINEL, self.rect, border_radius=8)
        cor_borda = COR_PAINEL_GLOW if self.focado else COR_PAINEL_BORDA
        espessura = 2 if self.focado else 1
        pygame.draw.rect(superficie, cor_borda, self.rect, width=espessura, border_radius=8)
        if self.texto:
            txt_surf = fonte.render(self.texto, True, COR_TEXTO_BRANCO)
        else:
            txt_surf = fonte.render(self.placeholder, True, COR_TEXTO_MUTED)
        superficie.blit(txt_surf, (self.rect.x + 14, self.rect.centery - txt_surf.get_height() // 2))
        if self.focado and self._cursor_visivel:
            largura_txt = fonte.size(self.texto)[0] if self.texto else 0
            cursor_x = self.rect.x + 14 + largura_txt + 2
            cursor_y1 = self.rect.centery - 12
            cursor_y2 = self.rect.centery + 12
            pygame.draw.line(superficie, COR_TEXTO_BRANCO, (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)
            pygame.draw.line(superficie, COR_TEXTO_BRANCO, (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)
