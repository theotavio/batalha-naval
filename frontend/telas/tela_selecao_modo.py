from __future__ import annotations
from typing import TYPE_CHECKING, Any
import pygame
from backend.constantes import ModoJogo
from frontend.core.constantes import LARGURA_TELA, ALTURA_TELA, COR_FUNDO, COR_PAINEL, COR_PAINEL_BORDA, COR_PRIMARIA, COR_TEXTO_BRANCO, COR_TEXTO_MUTED, COR_TEXTO_DOURADO
from frontend.core.gerenciador_assets import GerenciadorAssets
from frontend.core.gerenciador_som import GerenciadorSom
from frontend.componentes.botao import Botao
from frontend.telas.tela_base import TelaBase
if TYPE_CHECKING:
    from main import JogoPrincipal

class TelaSelecaoModo(TelaBase):

    def __init__(self, jogo: JogoPrincipal) -> None:
        super().__init__(jogo)
        self.assets = GerenciadorAssets.obter_instancia()
        self.som = GerenciadorSom.obter_instancia()
        self._criar_componentes()

    def _criar_componentes(self) -> None:
        btn_w = 480
        btn_h = 52
        inicio_y = 190
        espaco_y = 68
        centro_x = (LARGURA_TELA - btn_w) // 2
        self.btn_jxc = Botao((centro_x, inicio_y, btn_w, btn_h), texto='JOGADOR VS COMPUTADOR', on_click=lambda: self.jogo.mudar_tela('selecao_dificuldade', modo_jogo=ModoJogo.JOGADOR_VS_COMPUTADOR), cor_base=COR_PAINEL, tamanho_fonte='grande')
        self.btn_jxj = Botao((centro_x, inicio_y + espaco_y, btn_w, btn_h), texto='JOGADOR VS JOGADOR', on_click=lambda: self.jogo.mudar_tela('selecao_pvp'), cor_base=COR_PAINEL, tamanho_fonte='grande')
        self.btn_cxc = Botao((centro_x, inicio_y + espaco_y * 2, btn_w, btn_h), texto='SIMULAÇÃO COMPUTADOR VS COMPUTADOR', on_click=lambda: self.jogo.mudar_tela('selecao_dificuldade', modo_jogo=ModoJogo.COMPUTADOR_VS_COMPUTADOR), cor_base=COR_PAINEL, tamanho_fonte='media')
        self.btn_voltar = Botao(((LARGURA_TELA - 280) // 2, 635, 280, 48), texto='VOLTAR', on_click=lambda: self.jogo.voltar_tela(), cor_base=COR_PRIMARIA, tamanho_fonte='grande')
        self.botoes = [self.btn_jxc, self.btn_jxj, self.btn_cxc, self.btn_voltar]

    def inicializar(self, **kwargs: Any) -> None:
        self.som.tocar_musica('wowmenu')

    def processar_evento(self, evento: pygame.event.Event) -> None:
        for btn in self.botoes:
            btn.processar_evento(evento)

    def atualizar(self, dt: float) -> None:
        pass

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.fill(COR_FUNDO)
        fonte_tit = self.assets.obter_fonte('titulo', negrito=True)
        txt_tit = fonte_tit.render('SELECIONE O MODO DE BATALHA', True, COR_TEXTO_DOURADO)
        superficie.blit(txt_tit, ((LARGURA_TELA - txt_tit.get_width()) // 2, 70))
        fonte_sub = self.assets.obter_fonte('media')
        txt_sub = fonte_sub.render('Escolha as regras de combate e desafie oponentes humanos ou IA', True, COR_TEXTO_MUTED)
        superficie.blit(txt_sub, ((LARGURA_TELA - txt_sub.get_width()) // 2, 120))
        for btn in self.botoes:
            btn.desenhar(superficie)
