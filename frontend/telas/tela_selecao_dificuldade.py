from __future__ import annotations
from typing import TYPE_CHECKING, Any
import pygame
from backend.constantes import ModoJogo, DificuldadeIA
from frontend.core.constantes import LARGURA_TELA, ALTURA_TELA, COR_FUNDO, COR_PAINEL, COR_PAINEL_BORDA, COR_PRIMARIA, COR_SECUNDARIA, COR_SUCESSO, COR_PERIGO, COR_TEXTO_BRANCO, COR_TEXTO_MUTED, COR_TEXTO_DOURADO
from frontend.core.gerenciador_assets import GerenciadorAssets
from frontend.core.gerenciador_som import GerenciadorSom
from frontend.componentes.botao import Botao
from frontend.telas.tela_base import TelaBase
if TYPE_CHECKING:
    from main import JogoPrincipal

class TelaSelecaoDificuldade(TelaBase):

    def __init__(self, jogo: JogoPrincipal) -> None:
        super().__init__(jogo)
        self.assets = GerenciadorAssets.obter_instancia()
        self.som = GerenciadorSom.obter_instancia()
        self.modo_jogo: ModoJogo = ModoJogo.JOGADOR_VS_COMPUTADOR
        self.dificuldade_em_foco: DificuldadeIA = DificuldadeIA.MEDIA
        self._criar_componentes()

    def _criar_componentes(self) -> None:
        btn_w = 420
        btn_h = 50
        x_col1 = (LARGURA_TELA - (btn_w * 2 + 20)) // 2
        x_col2 = x_col1 + btn_w + 20
        y_lin1 = 150
        y_lin2 = 210
        self.btn_facil = Botao((x_col1, y_lin1, btn_w, btn_h), texto='FÁCIL', on_click=lambda: self._iniciar_partida(DificuldadeIA.FACIL), cor_base=COR_SUCESSO, tamanho_fonte='grande')
        self.btn_media = Botao((x_col2, y_lin1, btn_w, btn_h), texto='MÉDIO', on_click=lambda: self._iniciar_partida(DificuldadeIA.MEDIA), cor_base=COR_SECUNDARIA, tamanho_fonte='grande')
        self.btn_dificil = Botao((x_col1, y_lin2, btn_w, btn_h), texto='DIFÍCIL', on_click=lambda: self._iniciar_partida(DificuldadeIA.DIFICIL), cor_base=COR_PERIGO, tamanho_fonte='grande')
        self.btn_impossivel = Botao((x_col2, y_lin2, btn_w, btn_h), texto='IMPOSSÍVEL', on_click=lambda: self._iniciar_partida(DificuldadeIA.IMPOSSIVEL), cor_base=(150, 20, 60), tamanho_fonte='grande')
        self.btn_voltar = Botao(((LARGURA_TELA - 280) // 2, 635, 280, 48), texto='VOLTAR', on_click=lambda: self.jogo.voltar_tela(), cor_base=COR_PRIMARIA, tamanho_fonte='grande')
        self.botoes = [self.btn_facil, self.btn_media, self.btn_dificil, self.btn_impossivel, self.btn_voltar]

    def inicializar(self, **kwargs: Any) -> None:
        self.som.tocar_musica('wowmenu')
        self.modo_jogo = kwargs.get('modo_jogo', ModoJogo.JOGADOR_VS_COMPUTADOR)
        self.dificuldade_em_foco = DificuldadeIA.MEDIA

    def _iniciar_partida(self, dificuldade: DificuldadeIA) -> None:
        if self.modo_jogo == ModoJogo.COMPUTADOR_VS_COMPUTADOR:
            self.jogo.iniciar_partida_cxc(dificuldade=dificuldade)
        else:
            self.jogo.mudar_tela('posicionamento', modo_jogo=ModoJogo.JOGADOR_VS_COMPUTADOR, dificuldade=dificuldade)

    def processar_evento(self, evento: pygame.event.Event) -> None:
        for btn in self.botoes:
            btn.processar_evento(evento)
        if self.btn_facil.hover:
            self.dificuldade_em_foco = DificuldadeIA.FACIL
        elif self.btn_media.hover:
            self.dificuldade_em_foco = DificuldadeIA.MEDIA
        elif self.btn_dificil.hover:
            self.dificuldade_em_foco = DificuldadeIA.DIFICIL
        elif self.btn_impossivel.hover:
            self.dificuldade_em_foco = DificuldadeIA.IMPOSSIVEL

    def atualizar(self, dt: float) -> None:
        pass

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.fill(COR_FUNDO)
        fonte_tit = self.assets.obter_fonte('titulo', negrito=True)
        txt_tit = fonte_tit.render('ESCOLHA O NÍVEL DE DIFICULDADE', True, COR_TEXTO_DOURADO)
        superficie.blit(txt_tit, ((LARGURA_TELA - txt_tit.get_width()) // 2, 45))
        fonte_sub = self.assets.obter_fonte('media')
        txt_sub = fonte_sub.render('Passe o cursor sobre a dificuldade para visualizar as características táticas', True, COR_TEXTO_MUTED)
        superficie.blit(txt_sub, ((LARGURA_TELA - txt_sub.get_width()) // 2, 95))
        for btn in self.botoes:
            btn.desenhar(superficie)
        self._desenhar_painel_explicativo(superficie)

    def _desenhar_painel_explicativo(self, superficie: pygame.Surface) -> None:
        card_w, card_h = (920, 230)
        card_rect = pygame.Rect((LARGURA_TELA - card_w) // 2, 290, card_w, card_h)
        pygame.draw.rect(superficie, COR_PAINEL, card_rect, border_radius=12)
        pygame.draw.rect(superficie, COR_PAINEL_BORDA, card_rect, width=2, border_radius=12)
        fonte_tit = self.assets.obter_fonte('grande', negrito=True)
        fonte_tag = self.assets.obter_fonte('media', negrito=True)
        fonte_desc = self.assets.obter_fonte('media')
        tagline = ''
        if self.dificuldade_em_foco == DificuldadeIA.FACIL:
            titulo_nivel = 'NÍVEL FÁCIL: DISPAROS ALEATÓRIOS'
            cor_nivel = COR_SUCESSO
            linhas = ['• A IA realiza disparos aleatórios sem memorização tática.', '• Não investiga vizinhanças ao acertar uma embarcação.', '• Recomendado para quem está aprendendo as regras do jogo.']
        elif self.dificuldade_em_foco == DificuldadeIA.MEDIA:
            titulo_nivel = 'NÍVEL MÉDIO: CAÇA E ALVO COM PARIDADE'
            cor_nivel = COR_SECUNDARIA
            linhas = ['• A IA utiliza padrão xadrez de paridade para encontrar navios velozmente.', '• Ao acertar, investiga células ortogonais e persegue o alinhamento do navio.', '• Recomendado para uma partida equilibrada e dinâmica.']
        elif self.dificuldade_em_foco == DificuldadeIA.DIFICIL:
            titulo_nivel = 'NÍVEL DIFÍCIL: MAPA DE CALOR PROBABILÍSTICO'
            cor_nivel = COR_PERIGO
            linhas = ['• A IA calcula matriz de probabilidade geométrica em tempo real.', '• Posiciona sua própria frota com isolamento tático e dispersão nas bordas.', '• Ataca com precisão matemática as coordenadas mais prováveis.']
        else:
            titulo_nivel = 'NÍVEL IMPOSSÍVEL: MARECHAL ANTHONY'
            cor_nivel = (255, 60, 100)
            tagline = 'Que Deus esteja contigo!'
            linhas = ['• A IA é onisciente: conhece a posição de todos os seus navios e nunca erra um tiro.', '• A cada turno, suas embarcações não atingidas mudam de lugar em alto-mar.', '• Oponente supremo: você enfrentará o lendário Marechal Anthony.']
        txt_t = fonte_tit.render(titulo_nivel, True, cor_nivel)
        superficie.blit(txt_t, (card_rect.x + 24, card_rect.y + 16))
        y_lin = card_rect.y + 52
        if tagline:
            txt_tag = fonte_tag.render(tagline, True, COR_TEXTO_DOURADO)
            superficie.blit(txt_tag, (card_rect.x + 24, y_lin))
            y_lin += 28
        for l in linhas:
            txt_l = fonte_desc.render(l, True, COR_TEXTO_MUTED)
            superficie.blit(txt_l, (card_rect.x + 24, y_lin))
            y_lin += 28
