from __future__ import annotations
import time
from typing import TYPE_CHECKING, Any
import pygame
from backend.constantes import ModoJogo, EstadoPartida, ResultadoTiro
from backend.rede.protocolo import TipoMensagem
from backend.models.posicao import Posicao
from backend.models.jogada import Jogada
from backend.models.jogador import JogadorHumano, JogadorComputador, JogadorRemoto
from backend.servicos.gerenciador_partida import Partida
from backend.excecoes import JogadaRepetidaErro, PosicaoInvalidaErro
from frontend.core.constantes import LARGURA_TELA, ALTURA_TELA, COR_FUNDO, COR_PAINEL, COR_PAINEL_BORDA, COR_PRIMARIA, COR_SECUNDARIA, COR_SUCESSO, COR_PERIGO, COR_TEXTO_BRANCO, COR_TEXTO_MUTED, COR_TEXTO_DOURADO
from frontend.core.gerenciador_assets import GerenciadorAssets
from frontend.core.gerenciador_som import GerenciadorSom
from frontend.animacoes.particulas import SistemaParticulas
from frontend.animacoes.animacao_tiro import AnimacaoTiro
from frontend.componentes.botao import Botao
from frontend.componentes.modal import Modal
from frontend.componentes.tabuleiro_render import TabuleiroRender
from frontend.componentes.painel_historico import PainelHistorico
from frontend.telas.tela_base import TelaBase
if TYPE_CHECKING:
    from main import JogoPrincipal

class TelaPartida(TelaBase):

    def __init__(self, jogo: JogoPrincipal) -> None:
        super().__init__(jogo)
        self.assets = GerenciadorAssets.obter_instancia()
        self.som = GerenciadorSom.obter_instancia()
        self.sistema_particulas = SistemaParticulas()
        self.partida: Partida | None = None
        self.render_tabuleiro_esq: TabuleiroRender | None = None
        self.render_tabuleiro_dir: TabuleiroRender | None = None
        self.painel_historico = PainelHistorico(rect=(890, 85, 350, 525))
        self.animacao_tiro_atual: AnimacaoTiro | None = None
        self.modal_ativo: Modal | None = None
        self._aguardando_jogada_ia: bool = False
        self._timer_ia: float = 0.0
        self._delay_ia_segundos: float = 0.7
        self.cliente_rede: Any | None = None
        self.fim_de_jogo_exibido: bool = False
        self._criar_botoes()

    def _criar_botoes(self) -> None:
        self.btn_desistir = Botao((890, 625, 168, 44), texto='DESISTIR', on_click=self._solicitar_desistencia, cor_base=COR_PERIGO, tamanho_fonte='pequena')
        self.btn_pausar = Botao((1072, 625, 168, 44), texto='MENU / PAUSA', on_click=self._abrir_menu_pausa, cor_base=COR_PAINEL, tamanho_fonte='pequena')

    def inicializar(self, **kwargs: Any) -> None:
        self.partida = kwargs.get('partida')
        self.cliente_rede = kwargs.get('cliente_rede')
        if not self.partida:
            return
        self.sistema_particulas.limpar()
        self.animacao_tiro_atual = None
        self.modal_ativo = None
        self.fim_de_jogo_exibido = False
        self._aguardando_jogada_ia = False
        self.painel_historico.limpar()
        self.painel_historico.definir_jogadas(self.partida.historico_jogadas)
        self.som.tocar_musica('wowchapter1')
        j1 = self.partida.jogador1
        j2 = self.partida.jogador2
        revelar_j2 = isinstance(j1, JogadorComputador) and isinstance(j2, JogadorComputador)
        self.render_tabuleiro_esq = TabuleiroRender(x=45, y=85, tabuleiro=j1.tabuleiro, titulo=f'FROTA: {j1.nome.upper()}', revelar_navios=True, interativo=False)
        self.render_tabuleiro_dir = TabuleiroRender(x=465, y=85, tabuleiro=j2.tabuleiro, titulo=f'RADAR: {j2.nome.upper()}', revelar_navios=revelar_j2, interativo=True, on_celula_clicada=self._on_disparo_jogador_humano)
        if self.partida.estado == EstadoPartida.POSICIONAMENTO:
            self.partida.iniciar_partida()

    def _on_disparo_jogador_humano(self, posicao: Posicao) -> None:
        if not self.partida or self.partida.estado != EstadoPartida.EM_ANDAMENTO:
            return
        if self.animacao_tiro_atual and (not self.animacao_tiro_atual.finalizada):
            return
        jogador_vez = self.partida.jogador_da_vez
        if not jogador_vez.e_humano():
            return
        oponente = self.partida.obter_jogador_adversario(jogador_vez)
        if oponente.tabuleiro.foi_atacada(posicao):
            self.som.tocar_som('SoundMessageWarning')
            return
        if self.partida.modo_jogo == ModoJogo.JOGADOR_VS_JOGADOR_REDE and self.cliente_rede:
            self.cliente_rede.disparar_tiro(posicao.linha, posicao.coluna)
        self._disparar_com_animacao(atacante=jogador_vez, posicao=posicao)

    def _disparar_com_animacao(self, atacante: Any, posicao: Posicao) -> None:
        if not self.partida:
            return
        if atacante == self.partida.jogador1:
            origem = (240, 300)
            destino = self.render_tabuleiro_dir.obter_pixel_celula(posicao.linha, posicao.coluna)
        else:
            origem = (670, 300)
            destino = self.render_tabuleiro_esq.obter_pixel_celula(posicao.linha, posicao.coluna)
        try:
            jogada = self.partida.executar_jogada(posicao, atacante=atacante)
        except Exception:
            return

        def on_impacto() -> None:
            self.painel_historico.definir_jogadas(self.partida.historico_jogadas)
            self.painel_historico.rolar_para_o_fim()
            if self.partida.estado == EstadoPartida.FINALIZADA:
                self._exibir_fim_de_jogo()
        self.animacao_tiro_atual = AnimacaoTiro(origem=origem, destino=destino, resultado=jogada.resultado, sistema_particulas=self.sistema_particulas, on_impacto=on_impacto)

    def _processar_turno_ia(self, dt: float) -> None:
        if not self.partida or self.partida.estado != EstadoPartida.EM_ANDAMENTO:
            return
        if self.animacao_tiro_atual and (not self.animacao_tiro_atual.finalizada):
            return
        jogador_vez = self.partida.jogador_da_vez
        if isinstance(jogador_vez, JogadorComputador):
            if not self._aguardando_jogada_ia:
                self._aguardando_jogada_ia = True
                self._timer_ia = 0.0
            self._timer_ia += dt
            if self._timer_ia >= self._delay_ia_segundos:
                self._aguardando_jogada_ia = False
                oponente = self.partida.obter_jogador_adversario(jogador_vez)
                posicao_tiro = jogador_vez.escolher_jogada(oponente.tabuleiro)
                self._disparar_com_animacao(atacante=jogador_vez, posicao=posicao_tiro)

    def _exibir_fim_de_jogo(self) -> None:
        if self.fim_de_jogo_exibido or not self.partida:
            return
        self.fim_de_jogo_exibido = True
        resumo = self.partida.obter_resumo_fim_jogo()
        vencedor = resumo['vencedor']
        total_jogadas = resumo['total_jogadas']
        tempo_str = resumo['tempo_formatado']
        mensagem = f"VENCEDOR: {vencedor.upper()}!\n\n• Total de Disparos: {total_jogadas}\n• Duração da Partida: {tempo_str}\n• Aproveitamento {resumo['j1_nome']}: {resumo['j1_aproveitamento']}%\n• Aproveitamento {resumo['j2_nome']}: {resumo['j2_aproveitamento']}%"
        self.som.tocar_som('SoundMessageSuccess')
        self.modal_ativo = Modal(titulo='VITÓRIA NAVAL!', mensagem=mensagem, tipo='CONFIRMACAO', texto_confirmar='Ver Replay', texto_cancelar='Menu Principal', on_confirmar=lambda: self.jogo.mudar_tela('replays'), on_cancelar=lambda: self.jogo.mudar_tela('menu', registrar_historico=False), largura=520, altura=340)

    def _sair_para_menu(self) -> None:
        if self.cliente_rede:
            self.cliente_rede.desconectar()
        self.jogo.mudar_tela('menu', registrar_historico=False)

    def _solicitar_desistencia(self) -> None:
        if not self.partida or self.partida.estado != EstadoPartida.EM_ANDAMENTO:
            return
        self.partida.pausar()
        self.modal_ativo = Modal(titulo='CONFIRMAR DESISTÊNCIA', mensagem='Deseja render sua frota e declarar derrota?', tipo='CONFIRMACAO', texto_confirmar='Sim, Render-se', texto_cancelar='Continuar Lutando', on_confirmar=self._executar_desistencia, on_cancelar=self.partida.despausar)

    def _executar_desistencia(self) -> None:
        if not self.partida:
            return
        if self.partida.modo_jogo == ModoJogo.JOGADOR_VS_JOGADOR_REDE and self.cliente_rede:
            self.cliente_rede.desconectar()
        oponente = self.partida.obter_jogador_adversario(self.partida.jogador1)
        self.partida._finalizar_partida(vencedor=oponente)
        self._exibir_fim_de_jogo()

    def _abrir_menu_pausa(self) -> None:
        if not self.partida or self.partida.estado != EstadoPartida.EM_ANDAMENTO:
            return
        self.partida.pausar()
        self.modal_ativo = Modal(titulo='JOGO PAUSADO', mensagem='Batalha pausada. O que deseja fazer?', tipo='CONFIRMACAO', texto_confirmar='Retomar Jogo', texto_cancelar='Menu Principal', on_confirmar=self.partida.despausar, on_cancelar=self._sair_para_menu)

    def processar_evento(self, evento: pygame.event.Event) -> None:
        if self.modal_ativo and self.modal_ativo.ativo:
            self.modal_ativo.processar_evento(evento)
            return
        self.btn_desistir.processar_evento(evento)
        self.btn_pausar.processar_evento(evento)
        self.painel_historico.processar_evento(evento)
        if self.render_tabuleiro_dir:
            self.render_tabuleiro_dir.processar_evento(evento)

    def atualizar(self, dt: float) -> None:
        if self.modal_ativo and self.modal_ativo.ativo:
            self.modal_ativo.atualizar(dt)
            return
        self.sistema_particulas.atualizar(dt)
        if self.animacao_tiro_atual:
            self.animacao_tiro_atual.atualizar(dt)
        self._processar_turno_ia(dt)
        if self.partida and self.partida.modo_jogo == ModoJogo.JOGADOR_VS_JOGADOR_REDE and self.cliente_rede:
            self._processar_eventos_multiplayer()

    def _processar_eventos_multiplayer(self) -> None:
        if not self.cliente_rede or not self.partida:
            return
        if self.partida.estado != EstadoPartida.EM_ANDAMENTO:
            return
        if self.animacao_tiro_atual and (not self.animacao_tiro_atual.finalizada):
            return
        evento = self.cliente_rede.obter_evento()
        while evento is not None:
            tipo = evento.get('tipo')
            payload = evento.get('payload', {})
            if tipo == TipoMensagem.DISPARAR_TIRO.value:
                linha = payload.get('linha')
                coluna = payload.get('coluna')
                if linha is not None and coluna is not None:
                    pos = Posicao(linha, coluna)
                    self._disparar_com_animacao(atacante=self.partida.jogador2, posicao=pos)
                    return
            elif tipo == TipoMensagem.OPONENTE_DESCONECTOU.value:
                if self.partida.estado == EstadoPartida.EM_ANDAMENTO:
                    self.partida._finalizar_partida(vencedor=self.partida.jogador1)
                    self.som.tocar_som('SoundMessageSuccess')
                    self.modal_ativo = Modal(titulo='OPONENTE DESCONECTOU', mensagem='O adversário desconectou ou abandonou a partida.\nVocê venceu por desistência!', tipo='CONFIRMACAO', texto_confirmar='Ver Replay', texto_cancelar='Menu Principal', on_confirmar=lambda: self.jogo.mudar_tela('replays'), on_cancelar=self._sair_para_menu, largura=520, altura=320)
                return
            evento = self.cliente_rede.obter_evento()

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.fill(COR_FUNDO)
        self._desenhar_hud(superficie)
        if self.render_tabuleiro_esq:
            self.render_tabuleiro_esq.desenhar(superficie)
        if self.render_tabuleiro_dir:
            self.render_tabuleiro_dir.desenhar(superficie)
        self.painel_historico.desenhar(superficie)
        self.btn_desistir.desenhar(superficie)
        self.btn_pausar.desenhar(superficie)
        self.sistema_particulas.desenhar(superficie)
        if self.animacao_tiro_atual:
            self.animacao_tiro_atual.desenhar(superficie)
        if self.modal_ativo and self.modal_ativo.ativo:
            self.modal_ativo.desenhar(superficie)

    def _desenhar_hud(self, superficie: pygame.Surface) -> None:
        if not self.partida:
            return
        assets = GerenciadorAssets.obter_instancia()
        fonte_info = assets.obter_fonte('media', negrito=True)
        fonte_stats = assets.obter_fonte('pequena', negrito=True)
        hud_rect = pygame.Rect(45, 12, 1195, 58)
        pygame.draw.rect(superficie, COR_PAINEL, hud_rect, border_radius=10)
        pygame.draw.rect(superficie, COR_PAINEL_BORDA, hud_rect, width=2, border_radius=10)
        center_y = hud_rect.centery
        j1 = self.partida.jogador1
        j2 = self.partida.jogador2
        txt_j1_stats = fonte_stats.render(f'{j1.nome}: {j1.total_acertos} acertos ({j1.aproveitamento:.0f}%)', True, COR_TEXTO_BRANCO)
        superficie.blit(txt_j1_stats, (hud_rect.x + 20, center_y - txt_j1_stats.get_height() // 2))
        pill_tempo_rect = pygame.Rect(405, hud_rect.y + 10, 160, 38)
        pygame.draw.rect(superficie, (18, 24, 38), pill_tempo_rect, border_radius=6)
        pygame.draw.rect(superficie, COR_PAINEL_BORDA, pill_tempo_rect, width=1, border_radius=6)
        txt_tempo = fonte_info.render(f'TEMPO: {self.partida.tempo_formatado}', True, COR_TEXTO_DOURADO)
        superficie.blit(txt_tempo, (pill_tempo_rect.centerx - txt_tempo.get_width() // 2, center_y - txt_tempo.get_height() // 2))
        jogador_vez = self.partida.jogador_da_vez
        cor_vez = COR_SUCESSO if jogador_vez == self.partida.jogador1 else COR_SECUNDARIA
        texto_vez = f'TURNO {self.partida.turno_atual}: {jogador_vez.nome.upper()}'
        fonte_turno = assets.obter_fonte('media', negrito=True)
        if fonte_turno.size(texto_vez)[0] > 240:
            fonte_turno = assets.obter_fonte('pequena', negrito=True)
        txt_vez = fonte_turno.render(texto_vez, True, cor_vez)
        largura_turno = max(240, txt_vez.get_width() + 24)
        pill_turno_rect = pygame.Rect(580, hud_rect.y + 10, largura_turno, 38)
        pygame.draw.rect(superficie, (18, 24, 38), pill_turno_rect, border_radius=6)
        pygame.draw.rect(superficie, cor_vez, pill_turno_rect, width=1, border_radius=6)
        superficie.blit(txt_vez, (pill_turno_rect.centerx - txt_vez.get_width() // 2, center_y - txt_vez.get_height() // 2))
        txt_j2_stats = fonte_stats.render(f'{j2.nome}: {j2.total_acertos} acertos ({j2.aproveitamento:.0f}%)', True, COR_TEXTO_BRANCO)
        superficie.blit(txt_j2_stats, (hud_rect.right - txt_j2_stats.get_width() - 20, center_y - txt_j2_stats.get_height() // 2))
