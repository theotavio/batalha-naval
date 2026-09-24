from __future__ import annotations
import pygame
from backend.constantes import ResultadoTiro
from backend.models.jogada import Jogada
from frontend.core.constantes import COR_PAINEL, COR_PAINEL_BORDA, COR_PRIMARIA, COR_SUCESSO, COR_PERIGO, COR_SECUNDARIA, COR_TEXTO_BRANCO, COR_TEXTO_MUTED, COR_TEXTO_DOURADO
from frontend.core.gerenciador_assets import GerenciadorAssets

class PainelHistorico:

    def __init__(self, rect: tuple[int, int, int, int] | pygame.Rect) -> None:
        self.rect = pygame.Rect(rect)
        self.jogadas: list[Jogada] = []
        self.offset_scroll: int = 0
        self.item_altura: int = 42

    def definir_jogadas(self, jogadas: list[Jogada]) -> None:
        self.jogadas = jogadas

    def rolar_para_o_fim(self) -> None:
        total_altura = len(self.jogadas) * self.item_altura
        max_scroll = max(0, total_altura - (self.rect.height - 50))
        self.offset_scroll = max_scroll

    def processar_evento(self, evento: pygame.event.Event) -> bool:
        if evento.type == pygame.MOUSEWHEEL and self.rect.collidepoint(pygame.mouse.get_pos()):
            self.offset_scroll -= evento.y * 24
            total_altura = len(self.jogadas) * self.item_altura
            max_scroll = max(0, total_altura - (self.rect.height - 50))
            self.offset_scroll = max(0, min(self.offset_scroll, max_scroll))
            return True
        return False

    def desenhar(self, superficie: pygame.Surface) -> None:
        assets = GerenciadorAssets.obter_instancia()
        fonte_tit = assets.obter_fonte('grande', negrito=True)
        fonte_item = assets.obter_fonte('pequena')
        fonte_badge = assets.obter_fonte('pequena', negrito=True)
        pygame.draw.rect(superficie, COR_PAINEL, self.rect, border_radius=10)
        pygame.draw.rect(superficie, COR_PAINEL_BORDA, self.rect, width=2, border_radius=10)
        fonte_tit = assets.obter_fonte('media', negrito=True)
        txt_tit = fonte_tit.render('HISTÓRICO DE DISPAROS', True, COR_TEXTO_DOURADO)
        superficie.blit(txt_tit, (self.rect.centerx - txt_tit.get_width() // 2, self.rect.y + 12))
        pygame.draw.line(superficie, COR_PAINEL_BORDA, (self.rect.x + 10, self.rect.y + 40), (self.rect.right - 10, self.rect.y + 40), 1)
        area_lista = pygame.Rect(self.rect.x + 8, self.rect.y + 44, self.rect.width - 16, self.rect.height - 52)
        superficie_clip_antiga = superficie.get_clip()
        superficie.set_clip(area_lista)
        y_base = area_lista.y - self.offset_scroll
        for i, jogada in enumerate(self.jogadas):
            item_y = y_base + i * self.item_altura
            if item_y + self.item_altura < area_lista.y or item_y > area_lista.bottom:
                continue
            item_rect = pygame.Rect(area_lista.x, item_y, area_lista.width, self.item_altura - 4)
            pygame.draw.rect(superficie, (18, 24, 38), item_rect, border_radius=6)
            badge_rect = pygame.Rect(item_rect.x + 6, item_rect.y + 5, 36, 26)
            pygame.draw.rect(superficie, (32, 44, 64), badge_rect, border_radius=4)
            txt_t = fonte_badge.render(f'T{jogada.numero_turno}', True, COR_PRIMARIA)
            superficie.blit(txt_t, (badge_rect.centerx - txt_t.get_width() // 2, badge_rect.centery - txt_t.get_height() // 2))
            coord = jogada.posicao.para_coordenada()
            nome_resumido = jogada.jogador_nome[:9]
            txt_info = fonte_item.render(f'{nome_resumido} • {coord}', True, COR_TEXTO_BRANCO)
            superficie.blit(txt_info, (badge_rect.right + 8, item_rect.centery - txt_info.get_height() // 2))
            if jogada.resultado == ResultadoTiro.AFUNDADO:
                cor_res = COR_PERIGO
                texto_res = 'AFUNDOU!'
            elif jogada.resultado == ResultadoTiro.ACERTO:
                cor_res = COR_SECUNDARIA
                texto_res = 'ACERTOU'
            else:
                cor_res = COR_SUCESSO
                texto_res = 'ÁGUA'
            txt_res = fonte_badge.render(texto_res, True, cor_res)
            superficie.blit(txt_res, (item_rect.right - txt_res.get_width() - 8, item_rect.centery - txt_res.get_height() // 2))
        superficie.set_clip(superficie_clip_antiga)
