from __future__ import annotations
import copy
from typing import TYPE_CHECKING, Any
import pygame
from backend.constantes import TipoNavio, Orientacao, FROTA_PADRAO, ModoJogo, DificuldadeIA
from backend.rede.protocolo import TipoMensagem
from backend.models.posicao import Posicao
from backend.models.navio import Navio
from backend.models.tabuleiro import Tabuleiro
from frontend.core.constantes import LARGURA_TELA, ALTURA_TELA, COR_FUNDO, COR_PAINEL, COR_PAINEL_BORDA, COR_PRIMARIA, COR_SECUNDARIA, COR_SUCESSO, COR_PERIGO, COR_TEXTO_BRANCO, COR_TEXTO_MUTED, COR_TEXTO_DOURADO
from frontend.core.gerenciador_assets import GerenciadorAssets
from frontend.core.gerenciador_som import GerenciadorSom
from frontend.componentes.botao import Botao
from frontend.componentes.modal import Modal
from frontend.componentes.toast import Toast
from frontend.componentes.tabuleiro_render import TabuleiroRender
from frontend.telas.tela_base import TelaBase
if TYPE_CHECKING:
    from main import JogoPrincipal

class ItemDocaNavio:

    def __init__(self, tipo: TipoNavio, sprite_id: int) -> None:
        self.tipo = tipo
        self.sprite_id = sprite_id
        self.posicionado: bool = False
        self.navio_instancia: Navio | None = None

class TelaPosicionamento(TelaBase):

    def __init__(self, jogo: JogoPrincipal) -> None:
        super().__init__(jogo)
        self.assets = GerenciadorAssets.obter_instancia()
        self.som = GerenciadorSom.obter_instancia()
        self.tabuleiro_temp = Tabuleiro()
        self.render_tabuleiro = TabuleiroRender(x=50, y=105, tabuleiro=self.tabuleiro_temp, titulo='SEU TABULEIRO DEFENSIVO', revelar_navios=True, interativo=True, on_celula_clicada=self._on_celula_clicada, celula_tamanho=48)
        self.modo_jogo: ModoJogo = ModoJogo.JOGADOR_VS_COMPUTADOR
        self.dificuldade_ia: DificuldadeIA | None = DificuldadeIA.MEDIA
        self.cliente_rede: Any | None = None
        self.oponente_nome: str = 'Adversário'
        self.frota_enviada_rede: bool = False
        self.jogador_atual_num: int = 1
        self.tabuleiro_j1_pronto: Tabuleiro | None = None
        self.doca_navios: list[ItemDocaNavio] = []
        self.item_selecionado: ItemDocaNavio | None = None
        self.orientacao_atual: Orientacao = Orientacao.HORIZONTAL
        self.modal_ativo: Modal | None = None
        self.toast_ativo: Toast | None = None
        self._criar_botoes()

    def _criar_botoes(self) -> None:
        painel_x = 650
        btn_w = 580
        btn_h = 44
        self.btn_auto = Botao((painel_x, 370, btn_w, btn_h), texto='POSICIONAR AUTOMATICAMENTE', on_click=self._posicionar_automatico, cor_base=COR_PRIMARIA, tamanho_fonte='media')
        self.btn_girar = Botao((painel_x, 422, btn_w, btn_h), texto='GIRAR NAVIO (TECLA R / CLIQUE DIR.)', on_click=self._alternar_orientacao, cor_base=COR_PAINEL, tamanho_fonte='media')
        self.btn_limpar = Botao((painel_x, 474, btn_w, btn_h), texto='LIMPAR TABULEIRO', on_click=self._limpar_tabuleiro, cor_base=COR_PERIGO, tamanho_fonte='media')
        self.btn_confirmar = Botao((painel_x, 528, btn_w, 52), texto='CONFIRMAR E INICIAR BATALHA', on_click=self._confirmar_posicionamento, cor_base=COR_SUCESSO, tamanho_fonte='grande')
        self.btn_voltar = Botao((painel_x, 590, btn_w, 42), texto='VOLTAR', on_click=self._solicitar_voltar, cor_base=(45, 55, 72), tamanho_fonte='media')
        self.botoes = [self.btn_auto, self.btn_girar, self.btn_limpar, self.btn_confirmar, self.btn_voltar]

    def inicializar(self, **kwargs: Any) -> None:
        self.modo_jogo = kwargs.get('modo_jogo', ModoJogo.JOGADOR_VS_COMPUTADOR)
        self.dificuldade_ia = kwargs.get('dificuldade', DificuldadeIA.MEDIA)
        self.cliente_rede = kwargs.get('cliente_rede')
        self.oponente_nome = kwargs.get('oponente_nome', 'Adversário')
        self.frota_enviada_rede = False
        self.jogador_atual_num = 1
        self.tabuleiro_j1_pronto = None
        self.modal_ativo = None
        self.toast_ativo = None
        if self.modo_jogo == ModoJogo.JOGADOR_VS_JOGADOR_REDE:
            self.btn_confirmar.texto = 'CONFIRMAR E PRONTO'
        else:
            self.btn_confirmar.texto = 'CONFIRMAR E INICIAR BATALHA'
        self._reiniciar_doca()
        self.som.tocar_musica('wowoptions')

    def _reiniciar_doca(self) -> None:
        self.tabuleiro_temp.limpar()
        self.doca_navios.clear()
        self.item_selecionado = None
        self.orientacao_atual = Orientacao.HORIZONTAL
        for i, tipo in enumerate(FROTA_PADRAO):
            self.doca_navios.append(ItemDocaNavio(tipo=tipo, sprite_id=i + 1))
        if self.doca_navios:
            self.item_selecionado = self.doca_navios[0]
            self._atualizar_fantasma()

    def _atualizar_fantasma(self) -> None:
        if self.item_selecionado and (not self.item_selecionado.posicionado):
            self.render_tabuleiro.navio_fantasma = (self.item_selecionado.tipo, self.orientacao_atual)
        else:
            self.render_tabuleiro.navio_fantasma = None

    def _alternar_orientacao(self) -> None:
        self.orientacao_atual = Orientacao.VERTICAL if self.orientacao_atual == Orientacao.HORIZONTAL else Orientacao.HORIZONTAL
        self.som.tocar_som('SoundOptionChange')
        self._atualizar_fantasma()

    def _posicionar_automatico(self) -> None:
        self.tabuleiro_temp.posicionar_automaticamente()
        for i, navio in enumerate(self.tabuleiro_temp.navios):
            if i < len(self.doca_navios):
                self.doca_navios[i].posicionado = True
                self.doca_navios[i].navio_instancia = navio
        self.item_selecionado = None
        self._atualizar_fantasma()
        self.som.tocar_som('SoundMenuAccept')
        self.toast_ativo = Toast('Frota posicionada com sucesso!', tipo='SUCESSO')

    def _limpar_tabuleiro(self) -> None:
        self._reiniciar_doca()
        self.som.tocar_som('SoundUndo')
        self.toast_ativo = Toast('Tabuleiro limpo.', tipo='INFO')

    def _on_celula_clicada(self, pos: Posicao) -> None:
        navio_existente = self.tabuleiro_temp.obter_navio_na_posicao(pos)
        if navio_existente:
            self.tabuleiro_temp.remover_navio(navio_existente)
            for item in self.doca_navios:
                if item.navio_instancia == navio_existente:
                    item.posicionado = False
                    item.navio_instancia = None
                    self.item_selecionado = item
                    break
            self.som.tocar_som('SoundChoose')
            self._atualizar_fantasma()
            return
        if self.item_selecionado and (not self.item_selecionado.posicionado):
            tipo = self.item_selecionado.tipo
            if self.tabuleiro_temp.pode_posicionar(tipo, pos, self.orientacao_atual):
                novo_navio = Navio(tipo=tipo, posicao_inicial=pos, orientacao=self.orientacao_atual, sprite_id=self.item_selecionado.sprite_id)
                self.tabuleiro_temp.adicionar_navio(novo_navio)
                self.item_selecionado.posicionado = True
                self.item_selecionado.navio_instancia = novo_navio
                self.som.tocar_som('SoundMenuAccept')
                proximo = next((item for item in self.doca_navios if not item.posicionado), None)
                self.item_selecionado = proximo
                self._atualizar_fantasma()
            else:
                self.som.tocar_som('SoundMessageWarning')
                self.toast_ativo = Toast('Posição inválida ou com sobreposição!', tipo='ERRO')

    def _confirmar_posicionamento(self) -> None:
        nao_posicionados = [item for item in self.doca_navios if not item.posicionado]
        if nao_posicionados:
            self.som.tocar_som('SoundMessageError')
            self.modal_ativo = Modal(titulo='FROTA INCOMPLETA', mensagem=f'Ainda restam {len(nao_posicionados)} navios para posicionar!\nPosicione todos antes de confirmar.', tipo='AVISO')
            return
        if self.modo_jogo == ModoJogo.JOGADOR_VS_JOGADOR_REDE:
            if self.cliente_rede:
                self.cliente_rede.enviar_frota(self.tabuleiro_temp.para_dict())
                self.frota_enviada_rede = True
                self.btn_confirmar.desabilitado = True
                self.btn_confirmar.texto = 'AGUARDANDO OPONENTE...'
                self.som.tocar_som('SoundMenuAccept')
                self.modal_ativo = Modal(titulo='FROTA CONFIRMADA!', mensagem=f'Sua frota foi enviada ao servidor.\nAguardando {self.oponente_nome} finalizar a preparação...', tipo='AVISO', largura=520, altura=260)
            return
        if self.modo_jogo == ModoJogo.JOGADOR_VS_JOGADOR_LOCAL:
            if self.jogador_atual_num == 1:
                self.tabuleiro_j1_pronto = copy.deepcopy(self.tabuleiro_temp)
                self.jogador_atual_num = 2
                self._reiniciar_doca()
                self.modal_ativo = Modal(titulo='VEZ DO JOGADOR 2', mensagem='Jogador 1 pronto!\nPasse o controle para o Jogador 2 posicionar sua frota.', tipo='AVISO')
                return
            else:
                tab1 = self.tabuleiro_j1_pronto
                tab2 = copy.deepcopy(self.tabuleiro_temp)
                self.jogo.iniciar_partida_jxj_local(tab1, tab2)
                return
        elif self.modo_jogo == ModoJogo.JOGADOR_VS_COMPUTADOR:
            tab_humano = copy.deepcopy(self.tabuleiro_temp)
            self.jogo.iniciar_partida_jxc(tab_humano, self.dificuldade_ia)

    def _solicitar_voltar(self) -> None:
        if self.modo_jogo == ModoJogo.JOGADOR_VS_JOGADOR_REDE:
            self.modal_ativo = Modal(titulo='CANCELAR PREPARAÇÃO', mensagem='Deseja desistir da partida multiplayer e voltar ao menu?', tipo='CONFIRMACAO', on_confirmar=self._desistir_preparacao_rede)
        else:
            self.modal_ativo = Modal(titulo='CANCELAR PREPARAÇÃO', mensagem='Deseja desistir do posicionamento e voltar?', tipo='CONFIRMACAO', on_confirmar=lambda: self.jogo.voltar_tela())

    def _desistir_preparacao_rede(self) -> None:
        if self.cliente_rede:
            self.cliente_rede.desconectar()
        self.jogo.mudar_tela('multiplayer', registrar_historico=False)

    def processar_evento(self, evento: pygame.event.Event) -> None:
        if self.modal_ativo and self.modal_ativo.ativo:
            self.modal_ativo.processar_evento(evento)
            return
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
            self._alternar_orientacao()
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 3:
            self._alternar_orientacao()
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            self._verificar_clique_doca(evento.pos)
        self.render_tabuleiro.processar_evento(evento)
        for btn in self.botoes:
            btn.processar_evento(evento)

    def _verificar_clique_doca(self, mouse_pos: tuple[int, int]) -> None:
        painel_x = 650
        y_doca = 145
        mx, my = mouse_pos
        for i, item in enumerate(self.doca_navios):
            card_rect = pygame.Rect(painel_x + 12, y_doca + i * 34, 556, 30)
            if card_rect.collidepoint(mx, my):
                if item.posicionado and item.navio_instancia:
                    self.tabuleiro_temp.remover_navio(item.navio_instancia)
                    item.posicionado = False
                    item.navio_instancia = None
                self.item_selecionado = item
                self.som.tocar_som('SoundChoose')
                self._atualizar_fantasma()
                break

    def atualizar(self, dt: float) -> None:
        if self.modal_ativo and self.modal_ativo.ativo:
            self.modal_ativo.atualizar(dt)
        if self.toast_ativo and self.toast_ativo.ativo:
            self.toast_ativo.atualizar(dt)
        if self.modo_jogo == ModoJogo.JOGADOR_VS_JOGADOR_REDE and self.cliente_rede:
            self._processar_eventos_preparacao_rede()

    def _processar_eventos_preparacao_rede(self) -> None:
        evento = self.cliente_rede.obter_evento()
        while evento is not None:
            tipo = evento.get('tipo')
            payload = evento.get('payload', {})
            if tipo == TipoMensagem.FROTAS_CONFIRMADAS.value:
                self.modal_ativo = None
                self.som.tocar_som('SoundMessageSuccess')
                self.jogo.iniciar_partida_multiplayer(cliente_rede=self.cliente_rede, tabuleiro_local=copy.deepcopy(self.tabuleiro_temp), payload=payload)
                return
            elif tipo in (TipoMensagem.OPONENTE_DESCONECTOU.value, TipoMensagem.PARTIDA_CANCELADA.value):
                motivo = payload.get('motivo', 'O oponente desconectou durante a preparação.')
                self.modal_ativo = Modal(titulo='PARTIDA CANCELADA', mensagem=motivo, tipo='AVISO', on_confirmar=lambda: self.jogo.mudar_tela('multiplayer', registrar_historico=False), largura=500, altura=240)
                return
            elif tipo == TipoMensagem.ERRO.value:
                msg = payload.get('mensagem', 'Erro de conexão.')
                self.toast_ativo = Toast(msg, tipo='ERRO')
            evento = self.cliente_rede.obter_evento()

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.fill(COR_FUNDO)
        fonte_tit = self.assets.obter_fonte('titulo', negrito=True)
        nome_jogador = self.jogo.jogador_ativo_nome if self.jogador_atual_num == 1 else 'Jogador 2'
        txt_tit = fonte_tit.render(f'PREPARAÇÃO DE FROTA • {nome_jogador.upper()}', True, COR_TEXTO_DOURADO)
        superficie.blit(txt_tit, (50, 30))
        fonte_sub = self.assets.obter_fonte('media')
        txt_sub = fonte_sub.render("Posicione seus 2 Navios Grandes (4 posições) e 4 Navios Pequenos (2 posições). Pressione 'R' para girar.", True, COR_TEXTO_MUTED)
        superficie.blit(txt_sub, (50, 68))
        self.render_tabuleiro.desenhar(superficie)
        self._desenhar_doca(superficie)
        for btn in self.botoes:
            btn.desenhar(superficie)
        if self.toast_ativo and self.toast_ativo.ativo:
            self.toast_ativo.desenhar(superficie)
        if self.modal_ativo and self.modal_ativo.ativo:
            self.modal_ativo.desenhar(superficie)

    def _desenhar_doca(self, superficie: pygame.Surface) -> None:
        painel_x = 650
        painel_y = 105
        painel_w = 580
        painel_h = 250
        pygame.draw.rect(superficie, COR_PAINEL, (painel_x, painel_y, painel_w, painel_h), border_radius=10)
        pygame.draw.rect(superficie, COR_PAINEL_BORDA, (painel_x, painel_y, painel_w, painel_h), width=2, border_radius=10)
        fonte_h = self.assets.obter_fonte('grande', negrito=True)
        txt_h = fonte_h.render('DOCA DE EMBARCAÇÕES', True, COR_TEXTO_BRANCO)
        superficie.blit(txt_h, (painel_x + 16, painel_y + 10))
        fonte_item = self.assets.obter_fonte('media')
        fonte_status = self.assets.obter_fonte('pequena', negrito=True)
        for i, item in enumerate(self.doca_navios):
            card_y = painel_y + 40 + i * 34
            card_rect = pygame.Rect(painel_x + 12, card_y, painel_w - 24, 30)
            selecionado = self.item_selecionado == item
            cor_bg = (45, 60, 85) if selecionado else (20, 28, 44)
            pygame.draw.rect(superficie, cor_bg, card_rect, border_radius=4)
            if selecionado:
                pygame.draw.rect(superficie, COR_PRIMARIA, card_rect, width=2, border_radius=4)
            txt_nav = fonte_item.render(f'Navio {item.tipo.value} ({item.tipo.tamanho} células)', True, COR_TEXTO_BRANCO)
            superficie.blit(txt_nav, (card_rect.x + 10, card_rect.centery - txt_nav.get_height() // 2))
            if item.posicionado:
                coord_str = item.navio_instancia.posicao_inicial.para_coordenada() if item.navio_instancia else 'OK'
                txt_st = fonte_status.render(f'Posicionado em {coord_str}', True, COR_SUCESSO)
            else:
                txt_st = fonte_status.render('Disponível na Doca', True, COR_SECUNDARIA)
            superficie.blit(txt_st, (card_rect.right - txt_st.get_width() - 10, card_rect.centery - txt_st.get_height() // 2))
