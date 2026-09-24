from __future__ import annotations
from typing import TYPE_CHECKING, Any
import pygame
from frontend.core.constantes import LARGURA_TELA, ALTURA_TELA, COR_FUNDO, COR_PAINEL, COR_PAINEL_BORDA, COR_PRIMARIA, COR_SUCESSO, COR_PERIGO, COR_TEXTO_BRANCO, COR_TEXTO_MUTED, COR_TEXTO_DOURADO
from frontend.core.gerenciador_assets import GerenciadorAssets
from frontend.core.gerenciador_som import GerenciadorSom
from frontend.componentes.botao import Botao
from frontend.componentes.modal import Modal
from frontend.componentes.toast import Toast
from frontend.telas.tela_base import TelaBase
if TYPE_CHECKING:
    from main import JogoPrincipal

class TelaOpcoes(TelaBase):

    def __init__(self, jogo: JogoPrincipal) -> None:
        super().__init__(jogo)
        self.assets = GerenciadorAssets.obter_instancia()
        self.som = GerenciadorSom.obter_instancia()
        self.modal_ativo: Modal | None = None
        self.toast_ativo: Toast | None = None
        self._criar_componentes()

    def _criar_componentes(self) -> None:
        self.btn_modo_fullscreen = Botao((130, 165, 200, 48), texto='TELA CHEIA', on_click=lambda: self._definir_tela_cheia(True), cor_base=COR_PAINEL, tamanho_fonte='pequena')
        self.btn_modo_janela = Botao((350, 165, 200, 48), texto='MODO JANELA', on_click=lambda: self._definir_tela_cheia(False), cor_base=COR_SUCESSO, tamanho_fonte='pequena')
        self.btn_vol_geral_menos = Botao((645, 172, 34, 30), texto='-', on_click=lambda: self._alterar_volume('geral', -0.1), cor_base=COR_PAINEL, tamanho_fonte='grande')
        self.btn_vol_geral_mais = Botao((1048, 172, 34, 30), texto='+', on_click=lambda: self._alterar_volume('geral', 0.1), cor_base=COR_PAINEL, tamanho_fonte='grande')
        self.btn_vol_musica_menos = Botao((645, 237, 34, 30), texto='-', on_click=lambda: self._alterar_volume('musica', -0.1), cor_base=COR_PAINEL, tamanho_fonte='grande')
        self.btn_vol_musica_mais = Botao((1048, 237, 34, 30), texto='+', on_click=lambda: self._alterar_volume('musica', 0.1), cor_base=COR_PAINEL, tamanho_fonte='grande')
        self.btn_vol_efeitos_menos = Botao((645, 302, 34, 30), texto='-', on_click=lambda: self._alterar_volume('efeitos', -0.1), cor_base=COR_PAINEL, tamanho_fonte='grande')
        self.btn_vol_efeitos_mais = Botao((1048, 302, 34, 30), texto='+', on_click=lambda: self._alterar_volume('efeitos', 0.1), cor_base=COR_PAINEL, tamanho_fonte='grande')
        self.btn_vol_ui_menos = Botao((645, 367, 34, 30), texto='-', on_click=lambda: self._alterar_volume('interface', -0.1), cor_base=COR_PAINEL, tamanho_fonte='grande')
        self.btn_vol_ui_mais = Botao((1048, 367, 34, 30), texto='+', on_click=lambda: self._alterar_volume('interface', 0.1), cor_base=COR_PAINEL, tamanho_fonte='grande')
        self.btn_mudo = Botao((645, 425, 230, 40), texto='SILENCIAR ÁUDIO', on_click=self._alternar_mudo, cor_base=COR_PAINEL, tamanho_fonte='pequena')
        self.btn_resetar_banco = Botao((130, 465, 420, 46), texto='APAGAR ESTATÍSTICAS E CONTA', on_click=self._solicitar_reset_banco, cor_base=COR_PERIGO, tamanho_fonte='pequena')
        self.btn_voltar = Botao(((LARGURA_TELA - 280) // 2, 635, 280, 48), texto='VOLTAR', on_click=lambda: self.jogo.voltar_tela(), cor_base=COR_PRIMARIA, tamanho_fonte='grande')
        self.botoes = [self.btn_modo_fullscreen, self.btn_modo_janela, self.btn_vol_geral_menos, self.btn_vol_geral_mais, self.btn_vol_musica_menos, self.btn_vol_musica_mais, self.btn_vol_efeitos_menos, self.btn_vol_efeitos_mais, self.btn_vol_ui_menos, self.btn_vol_ui_mais, self.btn_mudo, self.btn_resetar_banco, self.btn_voltar]

    def inicializar(self, **kwargs: Any) -> None:
        self.modal_ativo = None
        self.toast_ativo = None
        self._atualizar_estado_botoes()

    def _atualizar_estado_botoes(self) -> None:
        if self.jogo.fullscreen:
            self.btn_modo_fullscreen.cor_base = COR_SUCESSO
            self.btn_modo_fullscreen.cor_texto = (0, 0, 0)
            self.btn_modo_janela.cor_base = COR_PAINEL
            self.btn_modo_janela.cor_texto = COR_TEXTO_MUTED
        else:
            self.btn_modo_janela.cor_base = COR_SUCESSO
            self.btn_modo_janela.cor_texto = (0, 0, 0)
            self.btn_modo_fullscreen.cor_base = COR_PAINEL
            self.btn_modo_fullscreen.cor_texto = COR_TEXTO_MUTED
        if self.som.mudo:
            self.btn_mudo.texto = 'REATIVAR ÁUDIO'
            self.btn_mudo.cor_base = COR_PERIGO
        else:
            self.btn_mudo.texto = 'SILENCIAR ÁUDIO'
            self.btn_mudo.cor_base = COR_PAINEL

    def _definir_tela_cheia(self, fullscreen: bool) -> None:
        self.jogo.definir_fullscreen(fullscreen)
        self._atualizar_estado_botoes()
        modo_str = 'Tela Cheia' if fullscreen else 'Modo Janela'
        self.toast_ativo = Toast(f'Modo de exibição: {modo_str}', tipo='SUCESSO')

    def _alterar_volume(self, canal: str, delta: float) -> None:
        if canal == 'geral':
            novo = round(self.som.volume_geral + delta, 1)
            self.som.definir_volume_geral(novo)
        elif canal == 'musica':
            novo = round(self.som.volume_musica + delta, 1)
            self.som.definir_volume_musica(novo)
        elif canal == 'efeitos':
            novo = round(self.som.volume_efeitos + delta, 1)
            self.som.definir_volume_efeitos(novo)
            self.som.tocar_som('cannon_fire')
        elif canal == 'interface':
            novo = round(self.som.volume_interface + delta, 1)
            self.som.definir_volume_interface(novo)
            self.som.tocar_som('SoundMenuMove')

    def _alternar_mudo(self) -> None:
        self.som.alternar_mudo()
        self._atualizar_estado_botoes()

    def _solicitar_reset_banco(self) -> None:
        self.modal_ativo = Modal(titulo='ÁREA DE RISCO: RESETAR DADOS', mensagem='ATENÇÃO: Esta ação é irreversível!\n\nTodos os perfis de jogadores, histórico de partidas, estatísticas\ne replays gravados serão permanentemente excluídos.\nO jogo retornará para a tela inicial de identificação.\n\nDeseja realmente apagar todos os dados?', tipo='CONFIRMACAO', texto_confirmar='Sim, Apagar Tudo', texto_cancelar='Cancelar', on_confirmar=self._executar_reset_banco, largura=560, altura=340)

    def _executar_reset_banco(self) -> None:
        self.jogo.repositorio.resetar_banco_de_dados()
        self.jogo.definir_jogador_ativo(1, 'Jogador')
        if 'splash' in self.jogo.telas:
            self.jogo.telas['splash'].campo_nome.texto = ''
        self.jogo.pilha_telas.clear()
        self.som.tocar_som('SoundMessageSuccess')
        self.jogo.mudar_tela('splash', registrar_historico=False)

    def processar_evento(self, evento: pygame.event.Event) -> None:
        if self.modal_ativo and self.modal_ativo.ativo:
            self.modal_ativo.processar_evento(evento)
            return
        for btn in self.botoes:
            btn.processar_evento(evento)

    def atualizar(self, dt: float) -> None:
        if self.modal_ativo and self.modal_ativo.ativo:
            self.modal_ativo.atualizar(dt)
        if self.toast_ativo and self.toast_ativo.ativo:
            self.toast_ativo.atualizar(dt)

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.fill(COR_FUNDO)
        fonte_tit = self.assets.obter_fonte('titulo', negrito=True)
        txt_tit = fonte_tit.render('OPÇÕES E CONFIGURAÇÕES', True, COR_TEXTO_DOURADO)
        superficie.blit(txt_tit, ((LARGURA_TELA - txt_tit.get_width()) // 2, 35))
        fonte_card = self.assets.obter_fonte('grande', negrito=True)
        fonte_label = self.assets.obter_fonte('media', negrito=True)
        fonte_val = self.assets.obter_fonte('pequena')
        fonte_pct = self.assets.obter_fonte('pequena', negrito=True)
        card_v_rect = pygame.Rect(100, 95, 480, 220)
        pygame.draw.rect(superficie, COR_PAINEL, card_v_rect, border_radius=12)
        pygame.draw.rect(superficie, COR_PAINEL_BORDA, card_v_rect, width=2, border_radius=12)
        txt_card_v = fonte_card.render('VÍDEO E EXIBIÇÃO', True, COR_PRIMARIA)
        superficie.blit(txt_card_v, (card_v_rect.x + 20, card_v_rect.y + 16))
        txt_modo_lbl = fonte_label.render('Modo de Tela:', True, COR_TEXTO_MUTED)
        superficie.blit(txt_modo_lbl, (130, 138))
        card_a_rect = pygame.Rect(620, 95, 560, 480)
        pygame.draw.rect(superficie, COR_PAINEL, card_a_rect, border_radius=12)
        pygame.draw.rect(superficie, COR_PAINEL_BORDA, card_a_rect, width=2, border_radius=12)
        txt_card_a = fonte_card.render('ÁUDIO E SONS ESPECÍFICOS', True, COR_PRIMARIA)
        superficie.blit(txt_card_a, (card_a_rect.x + 20, card_a_rect.y + 16))
        barras = [('Volume Geral (Master):', self.som.volume_geral, 150), ('Música de Fundo:', self.som.volume_musica, 215), ('Efeitos de Batalha (Canhões):', self.som.volume_efeitos, 280), ('Sons de Interface (Cliques):', self.som.volume_interface, 345)]
        for rotulo, vol, y_pos in barras:
            txt_rot = fonte_label.render(rotulo, True, COR_TEXTO_BRANCO)
            superficie.blit(txt_rot, (645, y_pos))
            bx = 688
            by = y_pos + 26
            bw = 350
            bh = 22
            pygame.draw.rect(superficie, (18, 24, 38), (bx, by, bw, bh), border_radius=5)
            largura_preenchida = int(bw * vol)
            if largura_preenchida > 0:
                pygame.draw.rect(superficie, COR_PRIMARIA, (bx, by, largura_preenchida, bh), border_radius=5)
            porcento_str = f'{int(vol * 100)}%'
            txt_pct = fonte_pct.render(porcento_str, True, COR_TEXTO_DOURADO)
            superficie.blit(txt_pct, (1092, y_pos + 28))
        card_r_rect = pygame.Rect(100, 335, 480, 240)
        pygame.draw.rect(superficie, COR_PAINEL, card_r_rect, border_radius=12)
        pygame.draw.rect(superficie, COR_PERIGO, card_r_rect, width=2, border_radius=12)
        txt_card_r = fonte_card.render('ÁREA DE RISCO', True, COR_PERIGO)
        superficie.blit(txt_card_r, (card_r_rect.x + 20, card_r_rect.y + 16))
        txt_r_info1 = fonte_val.render('Apagar todos os dados acumulados, histórico e conta.', True, COR_TEXTO_MUTED)
        txt_r_info2 = fonte_val.render('O jogo retornará para a tela inicial de identificação.', True, COR_TEXTO_MUTED)
        superficie.blit(txt_r_info1, (card_r_rect.x + 20, card_r_rect.y + 54))
        superficie.blit(txt_r_info2, (card_r_rect.x + 20, card_r_rect.y + 78))
        for btn in self.botoes:
            btn.desenhar(superficie)
        if self.toast_ativo and self.toast_ativo.ativo:
            self.toast_ativo.desenhar(superficie)
        if self.modal_ativo and self.modal_ativo.ativo:
            self.modal_ativo.desenhar(superficie)
