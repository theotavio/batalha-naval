from __future__ import annotations
import sys
import copy
from typing import Any
import pygame
from backend.constantes import ModoJogo, DificuldadeIA
from backend.models.tabuleiro import Tabuleiro
from backend.models.jogador import JogadorHumano, JogadorComputador, JogadorRemoto
from backend.ia.fabrica_ia import FabricaIA
from backend.servicos.gerenciador_partida import Partida
from backend.database.repositorio import Repositorio
from frontend.core.constantes import LARGURA_TELA, ALTURA_TELA, FPS, TITULO_JOGO, RESOLUCOES_DISPONIVEIS
from frontend.core.gerenciador_assets import GerenciadorAssets
from frontend.core.gerenciador_som import GerenciadorSom
from frontend.telas.tela_base import TelaBase
from frontend.telas.tela_splash_nome import TelaSplashNome
from frontend.telas.tela_menu import TelaMenu
from frontend.telas.tela_opcoes import TelaOpcoes
from frontend.telas.tela_selecao_modo import TelaSelecaoModo
from frontend.telas.tela_selecao_dificuldade import TelaSelecaoDificuldade
from frontend.telas.tela_selecao_pvp import TelaSelecaoPvP
from frontend.telas.tela_posicionamento import TelaPosicionamento
from frontend.telas.tela_partida import TelaPartida
from frontend.telas.tela_estatisticas import TelaEstatisticas
from frontend.telas.tela_replays import TelaReplays
from frontend.telas.tela_creditos import TelaCreditos
from frontend.telas.tela_multiplayer import TelaMultiplayer

class JogoPrincipal:

    def __init__(self) -> None:
        pygame.init()
        try:
            pygame.mixer.init()
        except Exception:
            pass
        self.fullscreen: bool = False
        self.resolucao_atual: tuple[int, int] = (LARGURA_TELA, ALTURA_TELA)
        self.tela = pygame.display.set_mode(self.resolucao_atual)
        self.canvas_virtual = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption(TITULO_JOGO)
        self.clock = pygame.time.Clock()
        self.rodando: bool = True
        self.repositorio = Repositorio()
        ultimo_jogador = self.repositorio.obter_ultimo_jogador()
        if ultimo_jogador:
            self.jogador_ativo_id: int = ultimo_jogador['id']
            self.jogador_ativo_nome: str = ultimo_jogador['nome']
            self.tela_atual_nome: str = 'menu'
        else:
            self.jogador_ativo_id = 1
            self.jogador_ativo_nome = 'Jogador'
            self.tela_atual_nome = 'splash'
        self.assets = GerenciadorAssets.obter_instancia()
        self.som = GerenciadorSom.obter_instancia()
        self.pilha_telas: list[str] = []
        self.telas: dict[str, TelaBase] = {'splash': TelaSplashNome(self), 'menu': TelaMenu(self), 'opcoes': TelaOpcoes(self), 'selecao_modo': TelaSelecaoModo(self), 'selecao_dificuldade': TelaSelecaoDificuldade(self), 'selecao_pvp': TelaSelecaoPvP(self), 'posicionamento': TelaPosicionamento(self), 'partida': TelaPartida(self), 'estatisticas': TelaEstatisticas(self), 'replays': TelaReplays(self), 'creditos': TelaCreditos(self), 'multiplayer': TelaMultiplayer(self)}
        self.tela_atual: TelaBase = self.telas[self.tela_atual_nome]
        self.tela_atual.inicializar()

    def definir_fullscreen(self, fullscreen: bool) -> None:
        self.fullscreen = fullscreen
        if self.fullscreen:
            try:
                self.tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                self.resolucao_atual = (self.tela.get_width(), self.tela.get_height())
            except Exception:
                self.fullscreen = False
                self.resolucao_atual = (LARGURA_TELA, ALTURA_TELA)
                self.tela = pygame.display.set_mode(self.resolucao_atual)
        else:
            self.resolucao_atual = (LARGURA_TELA, ALTURA_TELA)
            self.tela = pygame.display.set_mode(self.resolucao_atual)

    def definir_resolucao(self, resolucao: tuple[int, int]) -> None:
        self.resolucao_atual = resolucao
        self.fullscreen = False
        self.tela = pygame.display.set_mode(self.resolucao_atual)

    def definir_jogador_ativo(self, id_jogador: int, nome: str) -> None:
        self.jogador_ativo_id = id_jogador
        self.jogador_ativo_nome = nome
        self.repositorio.definir_configuracao('ultimo_jogador_id', str(id_jogador))

    def mudar_tela(self, nome_tela: str, registrar_historico: bool=True, **kwargs: Any) -> None:
        if registrar_historico and self.tela_atual_nome:
            if self.tela_atual_nome not in ('splash', nome_tela):
                self.pilha_telas.append(self.tela_atual_nome)
        if nome_tela in self.telas:
            self.tela_atual_nome = nome_tela
            self.tela_atual = self.telas[nome_tela]
            self.tela_atual.inicializar(**kwargs)

    def voltar_tela(self, **kwargs: Any) -> None:
        if self.pilha_telas:
            tela_anterior = self.pilha_telas.pop()
            self.mudar_tela(tela_anterior, registrar_historico=False, **kwargs)
        else:
            self.mudar_tela('menu', registrar_historico=False, **kwargs)

    def iniciar_partida_jxc(self, tabuleiro_humano: Tabuleiro, dificuldade: DificuldadeIA | None) -> None:
        j1 = JogadorHumano(nome=self.jogador_ativo_nome, id_jogador=self.jogador_ativo_id)
        j1.tabuleiro = tabuleiro_humano
        dif = dificuldade or DificuldadeIA.MEDIA
        nome_oponente = 'Marechal Anthony' if dif == DificuldadeIA.IMPOSSIVEL else 'Computador'
        ia = FabricaIA.criar(dif)
        j2 = JogadorComputador(nome=nome_oponente, ia=ia, id_jogador=999)
        if dif in (DificuldadeIA.DIFICIL, DificuldadeIA.IMPOSSIVEL):
            j2.tabuleiro.posicionar_estrategicamente()
        else:
            j2.tabuleiro.posicionar_automaticamente()
        partida = Partida(jogador1=j1, jogador2=j2, modo_jogo=ModoJogo.JOGADOR_VS_COMPUTADOR, dificuldade=dif, repositorio=self.repositorio)
        self.mudar_tela('partida', partida=partida)

    def iniciar_partida_jxj_local(self, tabuleiro_j1: Tabuleiro, tabuleiro_j2: Tabuleiro) -> None:
        j1 = JogadorHumano(nome=self.jogador_ativo_nome, id_jogador=self.jogador_ativo_id)
        j1.tabuleiro = tabuleiro_j1
        j2 = JogadorHumano(nome='Jogador 2', id_jogador=998)
        j2.tabuleiro = tabuleiro_j2
        partida = Partida(jogador1=j1, jogador2=j2, modo_jogo=ModoJogo.JOGADOR_VS_JOGADOR_LOCAL, repositorio=self.repositorio)
        self.mudar_tela('partida', partida=partida)

    def iniciar_partida_cxc(self, dificuldade: DificuldadeIA | None=None) -> None:
        dif = dificuldade or DificuldadeIA.DIFICIL
        nome1 = 'Marechal Anthony 1' if dif == DificuldadeIA.IMPOSSIVEL else 'Computador 1'
        nome2 = 'Marechal Anthony 2' if dif == DificuldadeIA.IMPOSSIVEL else 'Computador 2'
        ia1 = FabricaIA.criar(dif)
        j1 = JogadorComputador(nome=nome1, ia=ia1, id_jogador=901)
        ia2 = FabricaIA.criar(dif)
        j2 = JogadorComputador(nome=nome2, ia=ia2, id_jogador=902)
        if dif in (DificuldadeIA.DIFICIL, DificuldadeIA.IMPOSSIVEL):
            j1.tabuleiro.posicionar_estrategicamente()
            j2.tabuleiro.posicionar_estrategicamente()
        else:
            j1.tabuleiro.posicionar_automaticamente()
            j2.tabuleiro.posicionar_automaticamente()
        partida = Partida(jogador1=j1, jogador2=j2, modo_jogo=ModoJogo.COMPUTADOR_VS_COMPUTADOR, dificuldade=dif, repositorio=self.repositorio)
        self.mudar_tela('partida', partida=partida)

    def iniciar_partida_multiplayer(self, cliente_rede: Any, tabuleiro_local: Tabuleiro | None=None, payload: dict[str, Any] | None=None) -> None:
        j1 = JogadorHumano(nome=self.jogador_ativo_nome, id_jogador=self.jogador_ativo_id)
        if tabuleiro_local is not None:
            j1.tabuleiro = tabuleiro_local
        else:
            j1.tabuleiro.posicionar_automaticamente()
        oponente_nome = payload.get('oponente_nome', cliente_rede.oponente_nome) if payload else cliente_rede.oponente_nome
        j2 = JogadorRemoto(nome=oponente_nome, id_jogador=888)
        if payload and 'oponente_frota' in payload and payload['oponente_frota']:
            j2.tabuleiro = Tabuleiro.de_dict(payload['oponente_frota'])
        else:
            j2.tabuleiro.posicionar_automaticamente()
        partida = Partida(jogador1=j1, jogador2=j2, modo_jogo=ModoJogo.JOGADOR_VS_JOGADOR_REDE, repositorio=self.repositorio)
        sua_vez = payload.get('sua_vez', True) if payload else True
        if not sua_vez:
            partida.jogador_da_vez = j2
        self.mudar_tela('partida', partida=partida, cliente_rede=cliente_rede)

    def encerrar_jogo(self) -> None:
        self.rodando = False

    def _transformar_evento_mouse(self, evento: pygame.event.Event) -> pygame.event.Event:
        tela_w, tela_h = self.tela.get_size()
        escala_x = LARGURA_TELA / tela_w
        escala_y = ALTURA_TELA / tela_h
        if hasattr(evento, 'pos'):
            vx = int(evento.pos[0] * escala_x)
            vy = int(evento.pos[1] * escala_y)
            attr_dict = evento.__dict__.copy()
            attr_dict['pos'] = (vx, vy)
            if hasattr(evento, 'rel'):
                attr_dict['rel'] = (int(evento.rel[0] * escala_x), int(evento.rel[1] * escala_y))
            return pygame.event.Event(evento.type, attr_dict)
        return evento

    def executar(self) -> None:
        while self.rodando:
            dt = self.clock.tick(FPS) / 1000.0
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.encerrar_jogo()
                    break
                evento_virtual = self._transformar_evento_mouse(evento)
                self.tela_atual.processar_evento(evento_virtual)
            self.tela_atual.atualizar(dt)
            self.tela_atual.desenhar(self.canvas_virtual)
            if self.tela.get_size() == (LARGURA_TELA, ALTURA_TELA):
                self.tela.blit(self.canvas_virtual, (0, 0))
            else:
                superficie_escalada = pygame.transform.smoothscale(self.canvas_virtual, self.tela.get_size())
                self.tela.blit(superficie_escalada, (0, 0))
            pygame.display.flip()
        pygame.quit()
        sys.exit(0)
if __name__ == '__main__':
    jogo = JogoPrincipal()
    jogo.executar()
