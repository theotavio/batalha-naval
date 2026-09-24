from __future__ import annotations
import pygame
from frontend.core.constantes import LARGURA_TELA, ALTURA_TELA, COR_PAINEL, COR_SUCESSO, COR_PERIGO, COR_SECUNDARIA, COR_INFO, COR_TEXTO_BRANCO
from frontend.core.gerenciador_assets import GerenciadorAssets

class Toast:

    def __init__(self, mensagem: str, tipo: str='INFO', duracao: float=3.0) -> None:
        self.mensagem = mensagem
        self.tipo = tipo
        self.duracao = duracao
        self.tempo_vida: float = 0.0
        self.ativo: bool = True

    def atualizar(self, dt: float) -> bool:
        self.tempo_vida += dt
        if self.tempo_vida >= self.duracao:
            self.ativo = False
            return False
        return True

    def desenhar(self, superficie: pygame.Surface) -> None:
        if not self.ativo:
            return
        assets = GerenciadorAssets.obter_instancia()
        fonte = assets.obter_fonte('pequena', negrito=True)
        txt_surf = fonte.render(self.mensagem, True, COR_TEXTO_BRANCO)
        w = max(240, min(txt_surf.get_width() + 36, 560))
        h = 36
        x = (LARGURA_TELA - w) // 2
        y_base = ALTURA_TELA - h - 22
        t = self.tempo_vida
        anim_dur = 0.22
        if t < anim_dur:
            progresso = t / anim_dur
            y = int(ALTURA_TELA - (h + 24) * progresso)
        elif t > self.duracao - anim_dur:
            progresso = (self.duracao - t) / anim_dur
            y = int(ALTURA_TELA - (h + 24) * progresso)
        else:
            y = y_base
        cor_borda = COR_SUCESSO if self.tipo == 'SUCESSO' else COR_PERIGO if self.tipo == 'ERRO' else COR_SECUNDARIA if self.tipo == 'AVISO' else COR_INFO
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (*COR_PAINEL, 245), surf.get_rect(), border_radius=8)
        pygame.draw.rect(surf, cor_borda, surf.get_rect(), width=2, border_radius=8)
        surf.blit(txt_surf, ((w - txt_surf.get_width()) // 2, (h - txt_surf.get_height()) // 2))
        superficie.blit(surf, (x, y))
