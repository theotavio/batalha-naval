from __future__ import annotations
from typing import TYPE_CHECKING, Any
import pygame
from frontend.core.constantes import LARGURA_TELA, ALTURA_TELA, COR_FUNDO, COR_PAINEL, COR_PAINEL_BORDA, COR_PRIMARIA, COR_TEXTO_BRANCO, COR_TEXTO_MUTED, COR_TEXTO_DOURADO
from frontend.core.gerenciador_assets import GerenciadorAssets
from frontend.componentes.botao import Botao
from frontend.telas.tela_base import TelaBase
if TYPE_CHECKING:
    from main import JogoPrincipal

class TelaCreditos(TelaBase):

    def __init__(self, jogo: JogoPrincipal) -> None:
        super().__init__(jogo)
        self.assets = GerenciadorAssets.obter_instancia()
        self.btn_voltar = Botao(rect=((LARGURA_TELA - 280) // 2, 640, 280, 48), texto='VOLTAR', on_click=lambda: self.jogo.voltar_tela(), cor_base=COR_PRIMARIA, tamanho_fonte='grande')

    def processar_evento(self, evento: pygame.event.Event) -> None:
        self.btn_voltar.processar_evento(evento)

    def atualizar(self, dt: float) -> None:
        pass

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.fill(COR_FUNDO)
        fonte_tit = self.assets.obter_fonte('titulo', negrito=True)
        txt_tit = fonte_tit.render('CRÉDITOS E LICENÇAS', True, COR_TEXTO_DOURADO)
        superficie.blit(txt_tit, ((LARGURA_TELA - txt_tit.get_width()) // 2, 40))
        card_w, card_h = (960, 520)
        card_rect = pygame.Rect((LARGURA_TELA - card_w) // 2, 100, card_w, card_h)
        pygame.draw.rect(superficie, COR_PAINEL, card_rect, border_radius=14)
        pygame.draw.rect(superficie, COR_PAINEL_BORDA, card_rect, width=2, border_radius=14)
        fonte_secao = self.assets.obter_fonte('grande', negrito=True)
        fonte_texto = self.assets.obter_fonte('media')
        y_cursor = card_rect.y + 35
        secoes = [('SPRITES E ARTE GRÁFICA', ['Pirate Pack & Naval Assets por Kenney Vleugels (Kenney.nl)', 'Licença: Creative Commons Zero (CC0 1.0 Universal) - Domínio Público', 'Disponível em: https://www.kenney.nl']), ('EFEITOS SONOROS DE MENU E INTERFACE', ['"Menu sound effects", por Vircon32 (Carra)', 'Publicado em OpenGameArt sob licença Creative Commons Attribution (CC-BY 4.0)']), ('TRILHA SONORA NÁUTICA E EFEITOS DE CANHÕES', ['War on Water Soundtrack Tracks por HorrorPen', 'Publicado em OpenGameArt sob licença Creative Commons Attribution (CC-BY 3.0)', 'Disponível em: https://opengameart.org/content/war-on-water-tracks'])]
        for tit_sec, linhas in secoes:
            txt_s = fonte_secao.render(tit_sec, True, COR_PRIMARIA)
            superficie.blit(txt_s, (card_rect.x + 35, y_cursor))
            y_cursor += 36
            for l in linhas:
                txt_l = fonte_texto.render(l, True, COR_TEXTO_MUTED)
                superficie.blit(txt_l, (card_rect.x + 50, y_cursor))
                y_cursor += 28
            y_cursor += 22
        self.btn_voltar.desenhar(superficie)
