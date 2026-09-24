from __future__ import annotations
from typing import TYPE_CHECKING, Any
import pygame
from backend.servicos.gerenciador_replay import GerenciadorReplay
from frontend.core.constantes import LARGURA_TELA, ALTURA_TELA, COR_FUNDO, COR_PAINEL, COR_PAINEL_BORDA, COR_PAINEL_GLOW, COR_PRIMARIA, COR_PRIMARIA_HOVER, COR_SECUNDARIA, COR_SUCESSO, COR_PERIGO, COR_PERIGO_HOVER, COR_TEXTO_BRANCO, COR_TEXTO_MUTED, COR_TEXTO_DOURADO
from frontend.core.gerenciador_assets import GerenciadorAssets
from frontend.core.gerenciador_som import GerenciadorSom
from frontend.componentes.botao import Botao
from frontend.componentes.modal import Modal
from frontend.componentes.toast import Toast
from frontend.componentes.tabuleiro_render import TabuleiroRender
from frontend.componentes.painel_historico import PainelHistorico
from frontend.telas.tela_base import TelaBase
if TYPE_CHECKING:
    from main import JogoPrincipal

class TelaReplays(TelaBase):

    def __init__(self, jogo: JogoPrincipal) -> None:
        super().__init__(jogo)
        self.assets = GerenciadorAssets.obter_instancia()
        self.som = GerenciadorSom.obter_instancia()
        self.gerenciador_replay = GerenciadorReplay()
        self.lista_replays: list[dict[str, Any]] = []
        self.replay_selecionado: dict[str, Any] | None = None
        self.em_modo_player: bool = False
        self.render_tabuleiro_esq: TabuleiroRender | None = None
        self.render_tabuleiro_dir: TabuleiroRender | None = None
        self.painel_historico = PainelHistorico(rect=(890, 85, 350, 500))
        self.offset_scroll_lista: int = 0
        self.modal_ativo: Modal | None = None
        self.toast_ativo: Toast | None = None
        self._criar_botoes()

    def _criar_botoes(self) -> None:
        self.btn_reiniciar = Botao((45, 620, 95, 42), texto='INÍCIO', on_click=self._reiniciar_replay, cor_base=COR_PAINEL, tamanho_fonte='pequena')
        self.btn_voltar_passo = Botao((148, 620, 110, 42), texto='ANTERIOR', on_click=self._voltar_passo, cor_base=COR_PAINEL, tamanho_fonte='pequena')
        self.btn_play_pause = Botao((266, 620, 115, 42), texto='PLAY', on_click=self._alternar_play, cor_base=COR_PRIMARIA, tamanho_fonte='pequena')
        self.btn_avancar_passo = Botao((389, 620, 110, 42), texto='PRÓXIMO', on_click=self._avancar_passo, cor_base=COR_PAINEL, tamanho_fonte='pequena')
        self.btn_velocidade = Botao((507, 620, 140, 42), texto='VELOCIDADE: 1.0x', on_click=self._alternar_velocidade, cor_base=COR_SECUNDARIA, tamanho_fonte='pequena')
        self.btn_sair_player = Botao((655, 620, 150, 42), texto='LISTA REPLAYS', on_click=self._fechar_player, cor_base=(45, 55, 72), tamanho_fonte='pequena')
        self.btn_voltar_menu = Botao((360, 640, 240, 48), texto='VOLTAR', on_click=lambda: self.jogo.voltar_tela(), cor_base=COR_PRIMARIA, tamanho_fonte='grande')
        self.btn_limpar_todos = Botao((620, 640, 300, 48), texto='APAGAR TODOS OS REPLAYS', on_click=self._solicitar_limpar_todos_replays, cor_base=COR_PERIGO, tamanho_fonte='media')
        self.botoes_player = [self.btn_reiniciar, self.btn_voltar_passo, self.btn_play_pause, self.btn_avancar_passo, self.btn_velocidade, self.btn_sair_player]

    def inicializar(self, **kwargs: Any) -> None:
        self.som.tocar_musica('wowmenu')
        self._carregar_replays()
        self.em_modo_player = False
        self.replay_selecionado = None
        self.modal_ativo = None
        self.toast_ativo = None

    def _carregar_replays(self) -> None:
        self.lista_replays = self.jogo.repositorio.listar_replays(limite=40)

    def _abrir_replay(self, replay_resumo: dict[str, Any]) -> None:
        dados_completos = self.jogo.repositorio.obter_replay(replay_resumo['id'])
        if not dados_completos:
            return
        self.replay_selecionado = dados_completos
        self.gerenciador_replay.carregar_replay(dados_completos)
        self.em_modo_player = True
        j1_nome = dados_completos.get('jogador1_nome', 'Jogador 1')
        j2_nome = dados_completos.get('jogador2_nome', 'Jogador 2')
        self.render_tabuleiro_esq = TabuleiroRender(x=45, y=85, tabuleiro=self.gerenciador_replay.tabuleiro1, titulo=f'FROTA: {j1_nome.upper()}', revelar_navios=True, interativo=False)
        self.render_tabuleiro_dir = TabuleiroRender(x=465, y=85, tabuleiro=self.gerenciador_replay.tabuleiro2, titulo=f'FROTA: {j2_nome.upper()}', revelar_navios=True, interativo=False)
        self.btn_play_pause.texto = 'PLAY'
        self.painel_historico.definir_jogadas([])
        self.som.tocar_som('SoundPressStart')

    def _reiniciar_replay(self) -> None:
        self.gerenciador_replay.reiniciar()
        self.btn_play_pause.texto = 'PLAY'
        self.painel_historico.definir_jogadas([])

    def _voltar_passo(self) -> None:
        self.gerenciador_replay.voltar_passo()
        self._atualizar_historico_visivel()

    def _avancar_passo(self) -> None:
        self.gerenciador_replay.avancar_passo()
        self._atualizar_historico_visivel()

    def _alternar_play(self) -> None:
        rodando = self.gerenciador_replay.alternar_play_pause()
        self.btn_play_pause.texto = 'PAUSAR' if rodando else 'PLAY'

    def _alternar_velocidade(self) -> None:
        vel = self.gerenciador_replay.alternar_velocidade()
        self.btn_velocidade.texto = f'VELOCIDADE: {vel:.1f}x'

    def _fechar_player(self) -> None:
        self.em_modo_player = False
        self.replay_selecionado = None

    def _atualizar_historico_visivel(self) -> None:
        jogadas_ate_agora = self.gerenciador_replay.jogadas[:self.gerenciador_replay.indice_atual]
        self.painel_historico.definir_jogadas(jogadas_ate_agora)
        self.painel_historico.rolar_para_o_fim()

    def _solicitar_excluir_replay(self, replay_id: int, titulo: str) -> None:
        self.modal_ativo = Modal(titulo='EXCLUIR REPLAY', mensagem=f"Deseja realmente excluir a gravação:\n'{titulo}'?", tipo='CONFIRMACAO', texto_confirmar='Sim, Excluir', texto_cancelar='Cancelar', on_confirmar=lambda: self._executar_excluir_replay(replay_id), largura=520, altura=280)

    def _executar_excluir_replay(self, replay_id: int) -> None:
        sucesso = self.jogo.repositorio.excluir_replay(replay_id)
        if sucesso:
            self.som.tocar_som('SoundUndo')
            self._carregar_replays()
            self.toast_ativo = Toast('Replay excluído com sucesso!', tipo='INFO')
        else:
            self.som.tocar_som('SoundMessageError')
            self.toast_ativo = Toast('Falha ao excluir o replay.', tipo='ERRO')

    def _solicitar_limpar_todos_replays(self) -> None:
        if not self.lista_replays:
            return
        self.modal_ativo = Modal(titulo='APAGAR TODOS OS REPLAYS', mensagem='Deseja realmente apagar todas as gravações de replays salvas?\nEsta ação não poderá ser desfeita.', tipo='CONFIRMACAO', texto_confirmar='Sim, Apagar Todos', texto_cancelar='Cancelar', on_confirmar=self._executar_limpar_todos_replays, largura=560, altura=290)

    def _executar_limpar_todos_replays(self) -> None:
        total = self.jogo.repositorio.excluir_todos_replays()
        self.som.tocar_som('SoundUndo')
        self._carregar_replays()
        self.toast_ativo = Toast(f'{total} replays foram excluídos!', tipo='INFO')

    def processar_evento(self, evento: pygame.event.Event) -> None:
        if self.modal_ativo and self.modal_ativo.ativo:
            self.modal_ativo.processar_evento(evento)
            return
        if self.em_modo_player:
            for btn in self.botoes_player:
                btn.processar_evento(evento)
            self.painel_historico.processar_evento(evento)
        else:
            self.btn_voltar_menu.processar_evento(evento)
            if self.lista_replays:
                self.btn_limpar_todos.processar_evento(evento)
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                self._verificar_clique_item_replay(evento.pos)
            elif evento.type == pygame.MOUSEWHEEL:
                self.offset_scroll_lista = max(0, self.offset_scroll_lista - evento.y * 30)

    def _verificar_clique_item_replay(self, mouse_pos: tuple[int, int]) -> None:
        mx, my = mouse_pos
        item_w = 960
        lista_x = (LARGURA_TELA - item_w) // 2
        item_h = 72
        for i, rep in enumerate(self.lista_replays):
            item_y = 135 + i * (item_h + 10) - self.offset_scroll_lista
            if item_y < 115 or item_y > 595:
                continue
            item_rect = pygame.Rect(lista_x, item_y, item_w, item_h)
            btn_assistir_rect = pygame.Rect(item_rect.right - 235, item_rect.y + 18, 110, 36)
            btn_excluir_rect = pygame.Rect(item_rect.right - 115, item_rect.y + 18, 100, 36)
            if btn_assistir_rect.collidepoint(mx, my):
                self._abrir_replay(rep)
                break
            elif btn_excluir_rect.collidepoint(mx, my):
                self._solicitar_excluir_replay(rep['id'], rep['titulo'])
                break
            elif item_rect.collidepoint(mx, my):
                self._abrir_replay(rep)
                break

    def atualizar(self, dt: float) -> None:
        if self.modal_ativo and self.modal_ativo.ativo:
            self.modal_ativo.atualizar(dt)
            return
        if self.toast_ativo and self.toast_ativo.ativo:
            self.toast_ativo.atualizar(dt)
        if self.em_modo_player:
            jogada = self.gerenciador_replay.atualizar(dt)
            if jogada:
                self._atualizar_historico_visivel()
                if self.gerenciador_replay.finalizado:
                    self.btn_play_pause.texto = 'PLAY'

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.fill(COR_FUNDO)
        if self.em_modo_player:
            self._desenhar_player(superficie)
        else:
            self._desenhar_lista(superficie)
        if self.toast_ativo and self.toast_ativo.ativo:
            self.toast_ativo.desenhar(superficie)
        if self.modal_ativo and self.modal_ativo.ativo:
            self.modal_ativo.desenhar(superficie)

    def _desenhar_lista(self, superficie: pygame.Surface) -> None:
        fonte_tit = self.assets.obter_fonte('titulo', negrito=True)
        txt_tit = fonte_tit.render('REPLAYS E GRAVAÇÕES DE PARTIDAS', True, COR_TEXTO_DOURADO)
        superficie.blit(txt_tit, ((LARGURA_TELA - txt_tit.get_width()) // 2, 35))
        fonte_sub = self.assets.obter_fonte('media')
        txt_sub = fonte_sub.render('Selecione uma partida para reproduzir lance a lance ou gerencie gravações antigas', True, COR_TEXTO_MUTED)
        superficie.blit(txt_sub, ((LARGURA_TELA - txt_sub.get_width()) // 2, 80))
        item_w = 960
        lista_x = (LARGURA_TELA - item_w) // 2
        item_h = 72
        mouse_pos = pygame.mouse.get_pos()
        if not self.lista_replays:
            fonte_vazio = self.assets.obter_fonte('grande')
            txt_vazio = fonte_vazio.render('Nenhum replay encontrado ainda. Jogue uma partida!', True, COR_TEXTO_MUTED)
            superficie.blit(txt_vazio, ((LARGURA_TELA - txt_vazio.get_width()) // 2, 300))
        else:
            for i, rep in enumerate(self.lista_replays):
                item_y = 135 + i * (item_h + 10) - self.offset_scroll_lista
                if item_y < 110 or item_y > 600:
                    continue
                item_rect = pygame.Rect(lista_x, item_y, item_w, item_h)
                destaque = i == 0
                pygame.draw.rect(superficie, COR_PAINEL, item_rect, border_radius=10)
                cor_borda = COR_PAINEL_GLOW if destaque else COR_PAINEL_BORDA
                pygame.draw.rect(superficie, cor_borda, item_rect, width=2 if destaque else 1, border_radius=10)
                fonte_item_tit = self.assets.obter_fonte('media', negrito=True)
                prefixo = '[MAIS RECENTE] ' if destaque else ''
                titulo_limpo = str(rep.get('titulo', '')).split('(')[0].strip()
                titulo_formatado = f'{prefixo}{titulo_limpo}'
                txt_it = fonte_item_tit.render(titulo_formatado, True, COR_TEXTO_BRANCO)
                superficie.blit(txt_it, (item_rect.x + 18, item_rect.y + 14))
                fonte_info = self.assets.obter_fonte('pequena')
                data_str = str(rep.get('data_criacao', ''))[:16]
                info_str = f"Vencedor: {rep['vencedor_nome']} • {rep['total_jogadas']} jogadas • {rep['duracao_segundos']}s • {data_str}"
                txt_inf = fonte_info.render(info_str, True, COR_TEXTO_MUTED)
                superficie.blit(txt_inf, (item_rect.x + 18, item_rect.y + 42))
                btn_ass_rect = pygame.Rect(item_rect.right - 235, item_rect.y + 18, 110, 36)
                hover_ass = btn_ass_rect.collidepoint(mouse_pos)
                cor_ass = COR_PRIMARIA_HOVER if hover_ass else COR_PRIMARIA
                pygame.draw.rect(superficie, cor_ass, btn_ass_rect, border_radius=6)
                fonte_btn = self.assets.obter_fonte('pequena', negrito=True)
                txt_ass = fonte_btn.render('ASSISTIR', True, (0, 0, 0) if hover_ass else COR_TEXTO_BRANCO)
                superficie.blit(txt_ass, (btn_ass_rect.centerx - txt_ass.get_width() // 2, btn_ass_rect.centery - txt_ass.get_height() // 2))
                btn_exc_rect = pygame.Rect(item_rect.right - 115, item_rect.y + 18, 100, 36)
                hover_exc = btn_exc_rect.collidepoint(mouse_pos)
                cor_exc = COR_PERIGO_HOVER if hover_exc else COR_PERIGO
                pygame.draw.rect(superficie, cor_exc, btn_exc_rect, border_radius=6)
                txt_exc = fonte_btn.render('EXCLUIR', True, COR_TEXTO_BRANCO)
                superficie.blit(txt_exc, (btn_exc_rect.centerx - txt_exc.get_width() // 2, btn_exc_rect.centery - txt_exc.get_height() // 2))
        if not self.lista_replays:
            self.btn_voltar_menu.rect.x = (LARGURA_TELA - 240) // 2
            self.btn_voltar_menu.desenhar(superficie)
        else:
            self.btn_voltar_menu.rect.x = (LARGURA_TELA - 560) // 2
            self.btn_limpar_todos.rect.x = self.btn_voltar_menu.rect.right + 20
            self.btn_voltar_menu.desenhar(superficie)
            self.btn_limpar_todos.desenhar(superficie)

    def _desenhar_player(self, superficie: pygame.Surface) -> None:
        fonte_tit = self.assets.obter_fonte('grande', negrito=True)
        raw_tit = self.replay_selecionado.get('titulo', '') if self.replay_selecionado else ''
        titulo_limpo = str(raw_tit).split('(')[0].strip()
        txt_tit = fonte_tit.render(f'REPLAY: {titulo_limpo}', True, COR_TEXTO_DOURADO)
        superficie.blit(txt_tit, (45, 25))
        fonte_prog = self.assets.obter_fonte('media', negrito=True)
        prog_str = f'Lance: {self.gerenciador_replay.indice_atual} / {self.gerenciador_replay.total_jogadas}'
        txt_prog = fonte_prog.render(prog_str, True, COR_PRIMARIA)
        superficie.blit(txt_prog, (45, 55))
        if self.render_tabuleiro_esq:
            self.render_tabuleiro_esq.desenhar(superficie)
        if self.render_tabuleiro_dir:
            self.render_tabuleiro_dir.desenhar(superficie)
        self.painel_historico.desenhar(superficie)
        for btn in self.botoes_player:
            btn.desenhar(superficie)
