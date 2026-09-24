from __future__ import annotations
from typing import TYPE_CHECKING, Any
import pygame
from backend.constantes import ModoJogo
from frontend.core.constantes import LARGURA_TELA, ALTURA_TELA, COR_FUNDO, COR_PAINEL, COR_PAINEL_BORDA, COR_PRIMARIA, COR_SECUNDARIA, COR_SUCESSO, COR_TEXTO_BRANCO, COR_TEXTO_MUTED, COR_TEXTO_DOURADO
from frontend.core.gerenciador_assets import GerenciadorAssets
from frontend.core.gerenciador_som import GerenciadorSom
from frontend.componentes.botao import Botao
from frontend.telas.tela_base import TelaBase
if TYPE_CHECKING:
    from main import JogoPrincipal

class TelaSelecaoPvP(TelaBase):

    def __init__(self, jogo: JogoPrincipal) -> None:
        super().__init__(jogo)
        self.assets = GerenciadorAssets.obter_instancia()
        self.som = GerenciadorSom.obter_instancia()
        self._criar_componentes()

    def _criar_componentes(self) -> None:
        btn_w = 480
        btn_h = 48
        centro_x = (LARGURA_TELA - btn_w) // 2
        self.btn_local = Botao((100, 150, btn_w, btn_h), texto='JOGAR LOCALMENTE (MESMO COMPUTADOR)', on_click=self._iniciar_pvp_local, cor_base=COR_PRIMARIA, tamanho_fonte='media')
        self.btn_rede = Botao((700, 150, btn_w, btn_h), texto='JOGAR EM REDE (MATCHMAKING ONLINE)', on_click=self._iniciar_pvp_rede, cor_base=COR_SECUNDARIA, tamanho_fonte='media')
        self.btn_voltar = Botao(((LARGURA_TELA - 280) // 2, 635, 280, 48), texto='VOLTAR', on_click=lambda: self.jogo.voltar_tela(), cor_base=COR_PRIMARIA, tamanho_fonte='grande')
        self.botoes = [self.btn_local, self.btn_rede, self.btn_voltar]

    def inicializar(self, **kwargs: Any) -> None:
        self.som.tocar_musica('wowmenu')

    def _iniciar_pvp_local(self) -> None:
        self.jogo.mudar_tela('posicionamento', modo_jogo=ModoJogo.JOGADOR_VS_JOGADOR_LOCAL)

    def _iniciar_pvp_rede(self) -> None:
        self.jogo.mudar_tela('multiplayer')

    def processar_evento(self, evento: pygame.event.Event) -> None:
        for btn in self.botoes:
            btn.processar_evento(evento)

    def atualizar(self, dt: float) -> None:
        pass

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.fill(COR_FUNDO)
        fonte_tit = self.assets.obter_fonte('titulo', negrito=True)
        txt_tit = fonte_tit.render('MODO JOGADOR VS JOGADOR', True, COR_TEXTO_DOURADO)
        superficie.blit(txt_tit, ((LARGURA_TELA - txt_tit.get_width()) // 2, 35))
        fonte_sub = self.assets.obter_fonte('media')
        txt_sub = fonte_sub.render('Escolha entre disputar no mesmo computador ou via rede WebSocket', True, COR_TEXTO_MUTED)
        superficie.blit(txt_sub, ((LARGURA_TELA - txt_sub.get_width()) // 2, 85))
        for btn in self.botoes:
            btn.desenhar(superficie)
        self._desenhar_tutoriais(superficie)

    def _desenhar_tutoriais(self, superficie: pygame.Surface) -> None:
        card_w = 540
        card_h = 395
        card_y = 215
        fonte_card_tit = self.assets.obter_fonte('grande', negrito=True)
        fonte_passo_tit = self.assets.obter_fonte('pequena', negrito=True)
        fonte_passo_txt = self.assets.obter_fonte('pequena')
        rect_local = pygame.Rect(80, card_y, card_w, card_h)
        pygame.draw.rect(superficie, COR_PAINEL, rect_local, border_radius=12)
        pygame.draw.rect(superficie, COR_PAINEL_BORDA, rect_local, width=2, border_radius=12)
        txt_tl = fonte_card_tit.render('TUTORIAL: PARTIDA LOCAL', True, COR_PRIMARIA)
        superficie.blit(txt_tl, (rect_local.x + 22, rect_local.y + 16))
        passos_local = [('1. Posicionamento do Jogador 1:', 'Monte sua frota no tabuleiro e clique em Confirmar.'), ('2. Troca de Turno de Preparação:', 'O Jogador 2 assume o controle e posiciona seus navios.'), ('3. Batalha Alternada em Turnos:', 'A partida começa e cada jogador atira na sua vez.'), ('4. Dica Tática de Combate:', 'Mantenha sua frota em segredo durante a montagem!')]
        curr_y = rect_local.y + 58
        for tit, desc in passos_local:
            txt_p_tit = fonte_passo_tit.render(tit, True, COR_TEXTO_BRANCO)
            superficie.blit(txt_p_tit, (rect_local.x + 22, curr_y))
            curr_y += 22
            txt_p_desc = fonte_passo_txt.render(desc, True, COR_TEXTO_MUTED)
            superficie.blit(txt_p_desc, (rect_local.x + 22, curr_y))
            curr_y += 36
        rect_rede = pygame.Rect(660, card_y, card_w, card_h)
        pygame.draw.rect(superficie, COR_PAINEL, rect_rede, border_radius=12)
        pygame.draw.rect(superficie, COR_PAINEL_BORDA, rect_rede, width=2, border_radius=12)
        txt_tr = fonte_card_tit.render('TUTORIAL: PARTIDA EM REDE', True, COR_SECUNDARIA)
        superficie.blit(txt_tr, (rect_rede.x + 22, rect_rede.y + 16))
        passos_rede = [('1. Servidor Online na Nuvem:', 'URL oficial no Render configurada por padrao.'), ('2. Inicializacao do Servidor:', 'Se inativo, pode levar ~50s para acordar a instancia.'), ('3. Preparacao da Frota:', 'Apos aceitar, ambos posicionam seus navios.'), ('4. Batalha Sincronizada:', 'Disparos transmitidos em tempo real via WebSocket.')]
        curr_y = rect_rede.y + 58
        for tit, desc in passos_rede:
            txt_p_tit = fonte_passo_tit.render(tit, True, COR_TEXTO_BRANCO)
            superficie.blit(txt_p_tit, (rect_rede.x + 22, curr_y))
            curr_y += 22
            txt_p_desc = fonte_passo_txt.render(desc, True, COR_TEXTO_MUTED)
            superficie.blit(txt_p_desc, (rect_rede.x + 22, curr_y))
            curr_y += 36
