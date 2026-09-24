from __future__ import annotations
from typing import TYPE_CHECKING, Any
import pygame
from frontend.core.constantes import LARGURA_TELA, ALTURA_TELA, COR_FUNDO, COR_PAINEL, COR_PAINEL_BORDA, COR_PRIMARIA, COR_TEXTO_BRANCO, COR_TEXTO_MUTED, COR_TEXTO_DOURADO
from frontend.core.gerenciador_assets import GerenciadorAssets
from frontend.core.gerenciador_som import GerenciadorSom
from frontend.componentes.botao import Botao
from frontend.componentes.campo_texto import CampoTexto
from frontend.telas.tela_base import TelaBase
if TYPE_CHECKING:
    from main import JogoPrincipal

class TelaSplashNome(TelaBase):

    def __init__(self, jogo: JogoPrincipal) -> None:
        super().__init__(jogo)
        self.assets = GerenciadorAssets.obter_instancia()
        self.som = GerenciadorSom.obter_instancia()
        self.campo_nome = CampoTexto(rect=((LARGURA_TELA - 400) // 2, 360, 400, 52), texto_inicial='', placeholder='Digite seu nome...', max_caracteres=18, on_submit=self._confirmar_nome)
        self.campo_nome.focado = True
        self.btn_entrar = Botao(rect=((LARGURA_TELA - 260) // 2, 440, 260, 50), texto='ENTRAR NO JOGO', on_click=self._confirmar_nome, cor_base=COR_PRIMARIA, tamanho_fonte='grande')

    def inicializar(self, **kwargs: Any) -> None:
        self.som.tocar_musica('wowmenu')
        self.campo_nome.texto = ''
        self.campo_nome.focado = True

    def _confirmar_nome(self, nome_digitado: str | None=None) -> None:
        nome = (nome_digitado or self.campo_nome.texto).strip()
        if not nome:
            nome = 'Jogador'
        jogador_db = self.jogo.repositorio.obter_ou_criar_jogador(nome)
        self.jogo.definir_jogador_ativo(jogador_db['id'], jogador_db['nome'])
        self.som.tocar_som('SoundPressStart')
        self.jogo.mudar_tela('menu', registrar_historico=False)

    def processar_evento(self, evento: pygame.event.Event) -> None:
        self.campo_nome.processar_evento(evento)
        self.btn_entrar.processar_evento(evento)

    def atualizar(self, dt: float) -> None:
        self.campo_nome.atualizar(dt)

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.fill(COR_FUNDO)
        card_w, card_h = (600, 360)
        card_rect = pygame.Rect((LARGURA_TELA - card_w) // 2, 170, card_w, card_h)
        pygame.draw.rect(superficie, COR_PAINEL, card_rect, border_radius=16)
        pygame.draw.rect(superficie, COR_PAINEL_BORDA, card_rect, width=2, border_radius=16)
        fonte_destaque = self.assets.obter_fonte('destaque', negrito=True)
        txt_tit = fonte_destaque.render('BATALHA NAVAL', True, COR_TEXTO_DOURADO)
        superficie.blit(txt_tit, ((LARGURA_TELA - txt_tit.get_width()) // 2, 90))
        fonte_tit_card = self.assets.obter_fonte('grande', negrito=True)
        txt_identifique = fonte_tit_card.render('IDENTIFICAÇÃO DO JOGADOR', True, COR_TEXTO_BRANCO)
        superficie.blit(txt_identifique, ((LARGURA_TELA - txt_identifique.get_width()) // 2, card_rect.y + 36))
        fonte_info = self.assets.obter_fonte('media')
        txt_info = fonte_info.render('Digite seu nome para registrar suas estatísticas:', True, COR_TEXTO_MUTED)
        superficie.blit(txt_info, ((LARGURA_TELA - txt_info.get_width()) // 2, card_rect.y + 82))
        self.campo_nome.desenhar(superficie)
        self.btn_entrar.desenhar(superficie)
