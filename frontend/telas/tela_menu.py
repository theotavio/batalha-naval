from __future__ import annotations
from typing import TYPE_CHECKING, Any
import pygame
from frontend.core.constantes import LARGURA_TELA, ALTURA_TELA, COR_FUNDO, COR_PAINEL, COR_PAINEL_BORDA, COR_PRIMARIA, COR_PERIGO, COR_TEXTO_BRANCO, COR_TEXTO_MUTED, COR_TEXTO_DOURADO
from frontend.core.gerenciador_assets import GerenciadorAssets
from frontend.core.gerenciador_som import GerenciadorSom
from frontend.componentes.botao import Botao
from frontend.componentes.modal import Modal
from frontend.telas.tela_base import TelaBase
if TYPE_CHECKING:
    from main import JogoPrincipal

class TelaMenu(TelaBase):

    def __init__(self, jogo: JogoPrincipal) -> None:
        super().__init__(jogo)
        self.assets = GerenciadorAssets.obter_instancia()
        self.som = GerenciadorSom.obter_instancia()
        self.modal_ativo: Modal | None = None
        self._criar_botoes_menu()

    def _criar_botoes_menu(self) -> None:
        btn_w, btn_h = (380, 50)
        inicio_y = 200
        espaco_y = 62
        centro_x = (LARGURA_TELA - btn_w) // 2
        self.btn_novo_jogo = Botao((centro_x, inicio_y, btn_w, btn_h), texto='NOVO JOGO', on_click=lambda: self.jogo.mudar_tela('selecao_modo'), cor_base=COR_PRIMARIA, tamanho_fonte='grande')
        self.btn_opcoes = Botao((centro_x, inicio_y + espaco_y, btn_w, btn_h), texto='OPÇÕES', on_click=lambda: self.jogo.mudar_tela('opcoes'), cor_base=COR_PAINEL, tamanho_fonte='grande')
        self.btn_estatisticas = Botao((centro_x, inicio_y + espaco_y * 2, btn_w, btn_h), texto='ESTATÍSTICAS', on_click=lambda: self.jogo.mudar_tela('estatisticas'), cor_base=COR_PAINEL, tamanho_fonte='grande')
        self.btn_replays = Botao((centro_x, inicio_y + espaco_y * 3, btn_w, btn_h), texto='REPLAYS DE PARTIDAS', on_click=lambda: self.jogo.mudar_tela('replays'), cor_base=COR_PAINEL, tamanho_fonte='grande')
        self.btn_creditos = Botao((centro_x, inicio_y + espaco_y * 4, btn_w, btn_h), texto='CRÉDITOS', on_click=lambda: self.jogo.mudar_tela('creditos'), cor_base=COR_PAINEL, tamanho_fonte='grande')
        self.btn_sair = Botao((centro_x, inicio_y + espaco_y * 5, btn_w, btn_h), texto='SAIR DO JOGO', on_click=self._solicitar_saida, cor_base=COR_PERIGO, tamanho_fonte='grande')
        self.botoes = [self.btn_novo_jogo, self.btn_opcoes, self.btn_estatisticas, self.btn_replays, self.btn_creditos, self.btn_sair]

    def inicializar(self, **kwargs: Any) -> None:
        self.modal_ativo = None
        self.som.tocar_musica('wowmenu')

    def _solicitar_saida(self) -> None:
        self.modal_ativo = Modal(titulo='SAIR DO JOGO', mensagem='Deseja realmente encerrar a batalha e sair?', tipo='CONFIRMACAO', texto_confirmar='Sim, Sair', texto_cancelar='Permanecer', on_confirmar=self.jogo.encerrar_jogo)

    def processar_evento(self, evento: pygame.event.Event) -> None:
        if self.modal_ativo and self.modal_ativo.ativo:
            self.modal_ativo.processar_evento(evento)
            return
        for btn in self.botoes:
            btn.processar_evento(evento)

    def atualizar(self, dt: float) -> None:
        if self.modal_ativo and self.modal_ativo.ativo:
            self.modal_ativo.atualizar(dt)

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.fill(COR_FUNDO)
        fonte_destaque = self.assets.obter_fonte('destaque', negrito=True)
        txt_tit = fonte_destaque.render('BATALHA NAVAL', True, COR_TEXTO_DOURADO)
        superficie.blit(txt_tit, ((LARGURA_TELA - txt_tit.get_width()) // 2, 90))
        fonte_perfil = self.assets.obter_fonte('media', negrito=True)
        txt_perfil = fonte_perfil.render(f'Jogador: {self.jogo.jogador_ativo_nome}', True, COR_PRIMARIA)
        badge_w = max(200, txt_perfil.get_width() + 28)
        badge_rect = pygame.Rect(28, 24, badge_w, 38)
        pygame.draw.rect(superficie, COR_PAINEL, badge_rect, border_radius=8)
        pygame.draw.rect(superficie, COR_PAINEL_BORDA, badge_rect, width=2, border_radius=8)
        superficie.blit(txt_perfil, (badge_rect.centerx - txt_perfil.get_width() // 2, badge_rect.centery - txt_perfil.get_height() // 2))
        for btn in self.botoes:
            btn.desenhar(superficie)
        if self.modal_ativo and self.modal_ativo.ativo:
            self.modal_ativo.desenhar(superficie)
