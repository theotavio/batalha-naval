from __future__ import annotations
from typing import TYPE_CHECKING, Any
import pygame
from frontend.core.constantes import LARGURA_TELA, ALTURA_TELA, COR_FUNDO, COR_PAINEL, COR_PAINEL_BORDA, COR_PRIMARIA, COR_SECUNDARIA, COR_SUCESSO, COR_PERIGO, COR_TEXTO_BRANCO, COR_TEXTO_MUTED, COR_TEXTO_DOURADO
from frontend.core.gerenciador_assets import GerenciadorAssets
from frontend.core.gerenciador_som import GerenciadorSom
from frontend.componentes.botao import Botao
from frontend.telas.tela_base import TelaBase
if TYPE_CHECKING:
    from main import JogoPrincipal

class TelaEstatisticas(TelaBase):

    def __init__(self, jogo: JogoPrincipal) -> None:
        super().__init__(jogo)
        self.assets = GerenciadorAssets.obter_instancia()
        self.som = GerenciadorSom.obter_instancia()
        self.dados_estatisticas: dict[str, Any] = {}
        self.btn_voltar = Botao(rect=((LARGURA_TELA - 280) // 2, 640, 280, 48), texto='VOLTAR', on_click=lambda: self.jogo.voltar_tela(), cor_base=COR_PRIMARIA, tamanho_fonte='grande')

    def inicializar(self, **kwargs: Any) -> None:
        self.som.tocar_musica('wowmenu')
        self.dados_estatisticas = self.jogo.repositorio.obter_estatisticas_jogador(self.jogo.jogador_ativo_id)

    def processar_evento(self, evento: pygame.event.Event) -> None:
        self.btn_voltar.processar_evento(evento)

    def atualizar(self, dt: float) -> None:
        pass

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.fill(COR_FUNDO)
        fonte_tit = self.assets.obter_fonte('titulo', negrito=True)
        txt_tit = fonte_tit.render('ESTATÍSTICAS DE COMBATE', True, COR_TEXTO_DOURADO)
        superficie.blit(txt_tit, ((LARGURA_TELA - txt_tit.get_width()) // 2, 40))
        fonte_nome = self.assets.obter_fonte('grande', negrito=True)
        txt_nome = fonte_nome.render(f'Jogador: {self.jogo.jogador_ativo_nome}', True, COR_PRIMARIA)
        superficie.blit(txt_nome, ((LARGURA_TELA - txt_nome.get_width()) // 2, 85))
        recorde_val = self.dados_estatisticas.get('menor_jogadas_vitoria')
        recorde_str = f'{recorde_val} jogadas' if recorde_val else '-'
        cards = [('PARTIDAS JOGADAS', str(self.dados_estatisticas.get('partidas_jogadas', 0)), COR_PRIMARIA), ('VITÓRIAS NAVAIS', str(self.dados_estatisticas.get('vitorias', 0)), COR_SUCESSO), ('DERROTAS', str(self.dados_estatisticas.get('derrotas', 0)), COR_PERIGO), ('TOTAL DE ACERTOS', str(self.dados_estatisticas.get('acertos', 0)), COR_SECUNDARIA), ('TIROS NA ÁGUA', str(self.dados_estatisticas.get('erros', 0)), COR_TEXTO_MUTED), ('APROVEITAMENTO', f"{self.dados_estatisticas.get('aproveitamento', 0.0):.1f}%", COR_TEXTO_DOURADO), ('MAIOR SEQUÊNCIA', f"{self.dados_estatisticas.get('maior_sequencia_acertos', 0)} tiros", COR_SUCESSO), ('RECORDE DE EFICIÊNCIA', recorde_str, COR_PRIMARIA)]
        card_w = 265
        card_h = 92
        cols = 4
        inicio_x = (LARGURA_TELA - (cols * (card_w + 16) - 16)) // 2
        inicio_y = 145
        fonte_rotulo = self.assets.obter_fonte('pequena', negrito=True)
        fonte_val = self.assets.obter_fonte('grande', negrito=True)
        for i, (rotulo, valor, cor_destaque) in enumerate(cards):
            col = i % cols
            lin = i // cols
            cx = inicio_x + col * (card_w + 16)
            cy = inicio_y + lin * (card_h + 16)
            card_rect = pygame.Rect(cx, cy, card_w, card_h)
            pygame.draw.rect(superficie, COR_PAINEL, card_rect, border_radius=10)
            pygame.draw.rect(superficie, COR_PAINEL_BORDA, card_rect, width=2, border_radius=10)
            txt_r = fonte_rotulo.render(rotulo, True, COR_TEXTO_MUTED)
            superficie.blit(txt_r, (cx + 16, cy + 14))
            txt_v = fonte_val.render(valor, True, cor_destaque)
            superficie.blit(txt_v, (cx + 16, cy + 42))
        info_rect = pygame.Rect(inicio_x, 380, cols * (card_w + 16) - 16, 160)
        pygame.draw.rect(superficie, COR_PAINEL, info_rect, border_radius=12)
        pygame.draw.rect(superficie, COR_PAINEL_BORDA, info_rect, width=2, border_radius=12)
        fonte_info_tit = self.assets.obter_fonte('grande', negrito=True)
        txt_it = fonte_info_tit.render('RESUMO TÁTICO E PROGRESSÃO', True, COR_TEXTO_BRANCO)
        superficie.blit(txt_it, (info_rect.x + 24, info_rect.y + 18))
        p_jogadas = self.dados_estatisticas.get('partidas_jogadas', 0)
        vitorias = self.dados_estatisticas.get('vitorias', 0)
        taxa_vit = vitorias / p_jogadas * 100.0 if p_jogadas > 0 else 0.0
        fonte_detalhe = self.assets.obter_fonte('media')
        linhas_detalhe = [f'• Taxa de Vitória Geral: {taxa_vit:.1f}% de vitórias em combate.', f"• Precisão de Artilharia: {self.dados_estatisticas.get('aproveitamento', 0.0):.1f}% dos disparos atingiram embarcações inimigas."]
        cur_y = info_rect.y + 60
        for l in linhas_detalhe:
            txt_l = fonte_detalhe.render(l, True, COR_TEXTO_MUTED)
            superficie.blit(txt_l, (info_rect.x + 24, cur_y))
            cur_y += 32
        self.btn_voltar.desenhar(superficie)
