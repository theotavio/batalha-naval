from __future__ import annotations
import time
from typing import TYPE_CHECKING, Any
import pygame
from backend.constantes import ModoJogo
from backend.rede.protocolo import TipoMensagem
from backend.rede.cliente_rede import ClienteRede
from frontend.core.constantes import LARGURA_TELA, ALTURA_TELA, COR_FUNDO, COR_PAINEL, COR_PAINEL_BORDA, COR_PAINEL_GLOW, COR_PRIMARIA, COR_SECUNDARIA, COR_SUCESSO, COR_PERIGO, COR_TEXTO_BRANCO, COR_TEXTO_MUTED, COR_TEXTO_DOURADO
from frontend.core.gerenciador_assets import GerenciadorAssets
from frontend.core.gerenciador_som import GerenciadorSom
from frontend.componentes.botao import Botao
from frontend.componentes.campo_texto import CampoTexto
from frontend.componentes.modal import Modal
from frontend.componentes.toast import Toast
from frontend.telas.tela_base import TelaBase
if TYPE_CHECKING:
    from main import JogoPrincipal

class TelaMultiplayer(TelaBase):

    def __init__(self, jogo: JogoPrincipal) -> None:
        super().__init__(jogo)
        self.assets = GerenciadorAssets.obter_instancia()
        self.som = GerenciadorSom.obter_instancia()
        self.cliente_rede = ClienteRede()
        self.em_fila: bool = False
        self.tempo_busca: float = 0.0
        self.modal_ativo: Modal | None = None
        self.toast_ativo: Toast | None = None
        self.campo_servidor = CampoTexto(rect=((LARGURA_TELA - 520) // 2, 205, 520, 46), texto_inicial='wss://batalha-naval-hmgi.onrender.com', placeholder='Endereço do Servidor...', max_caracteres=120)
        self._criar_botoes()

    def _criar_botoes(self) -> None:
        cx = (LARGURA_TELA - 520) // 2
        self.btn_entrar_fila = Botao((cx, 345, 520, 50), texto='BUSCAR PARTIDA (MATCHMAKING)', on_click=self._alternar_fila, cor_base=COR_PRIMARIA, tamanho_fonte='grande')
        self.btn_iniciar_servidor_local = Botao((cx, 405, 520, 44), texto='INICIAR SERVIDOR LOCAL (PORTA 8765)', on_click=self._iniciar_servidor_local, cor_base=COR_PAINEL, tamanho_fonte='media')
        self.btn_voltar = Botao((cx, 458, 520, 44), texto='VOLTAR', on_click=self._voltar_menu, cor_base=(45, 55, 72), tamanho_fonte='grande')
        self.botoes = [self.btn_entrar_fila, self.btn_iniciar_servidor_local, self.btn_voltar]

    def inicializar(self, **kwargs: Any) -> None:
        self.som.tocar_musica('wowoptions')
        self.em_fila = False
        self.tempo_busca = 0.0
        self.modal_ativo = None
        self.toast_ativo = None
        self.btn_entrar_fila.texto = 'BUSCAR PARTIDA (MATCHMAKING)'
        self.btn_entrar_fila.cor_base = COR_PRIMARIA

    def _normalizar_url(self, texto: str) -> str:
        url = texto.strip()
        if not url:
            return 'ws://127.0.0.1:8765'
        url = url.replace(' ', '').rstrip('/')
        if url.startswith('https://'):
            url = 'wss://' + url[len('https://'):]
        elif url.startswith('http://'):
            url = 'ws://' + url[len('http://'):]
        elif url.startswith('tcp://'):
            url = 'ws://' + url[len('tcp://'):]
        if '127.0.0.0' in url:
            url = url.replace('127.0.0.0', '127.0.0.1')
        elif '0.0.0.0' in url:
            url = url.replace('0.0.0.0', '127.0.0.1')
        raw_host = url
        if '://' in raw_host:
            raw_host = raw_host.split('://', 1)[1]
        raw_host = raw_host.split('/', 1)[0]
        host_sem_porta = raw_host.split(':', 1)[0]
        partes_ip = host_sem_porta.split('.')
        e_ip_numerico = len(partes_ip) == 4 and all((p.isdigit() for p in partes_ip))
        e_localhost = host_sem_porta.lower() == 'localhost'
        if not (url.startswith('ws://') or url.startswith('wss://')):
            if e_ip_numerico or e_localhost:
                url = f'ws://{url}'
            else:
                url = f'wss://{url}'
        if ':' not in raw_host:
            if e_ip_numerico or e_localhost:
                url = f'{url}:8765'
        return url

    def _iniciar_servidor_local(self) -> None:
        import threading
        import asyncio
        import logging
        from backend.rede.servidor_matchmaking import ServidorMatchmaking, esta_servidor_rodando
        if esta_servidor_rodando(porta=8765):
            self.som.tocar_som('SoundMessageSuccess')
            self.toast_ativo = Toast('Servidor local já está em execução na porta 8765!', tipo='INFO')
            return

        def rodar():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            servidor = ServidorMatchmaking(host='0.0.0.0', porta=8765)
            try:
                loop.run_until_complete(servidor.iniciar())
                loop.run_forever()
            except OSError as e:
                logging.getLogger('ServidorMatchmaking').warning(f'Porta 8765 já em uso: {e}')
            except Exception as e:
                logging.getLogger('ServidorMatchmaking').error(f'Erro no servidor: {e}')
        t = threading.Thread(target=rodar, daemon=True)
        t.start()
        time.sleep(0.1)
        self.som.tocar_som('SoundMessageSuccess')
        self.toast_ativo = Toast('Servidor local iniciado na porta 8765!', tipo='SUCESSO')

    def _alternar_fila(self) -> None:
        if not self.em_fila:
            url = self._normalizar_url(self.campo_servidor.texto)
            self.campo_servidor.texto = url
            self.cliente_rede.conectar(url, self.jogo.jogador_ativo_nome)
            self.em_fila = True
            self.tempo_busca = 0.0
            self.btn_entrar_fila.texto = 'CANCELAR BUSCA'
            self.btn_entrar_fila.cor_base = COR_PERIGO
            self.som.tocar_som('SoundPressStart')
            self.toast_ativo = Toast('Conectando ao servidor...', tipo='INFO')
        else:
            self.cliente_rede.sair_fila()
            self.cliente_rede.desconectar()
            self.em_fila = False
            self.tempo_busca = 0.0
            self.btn_entrar_fila.texto = 'BUSCAR PARTIDA (MATCHMAKING)'
            self.btn_entrar_fila.cor_base = COR_PRIMARIA
            self.som.tocar_som('SoundMenuCancel')
            self.toast_ativo = Toast('Busca de partida cancelada.', tipo='INFO')

    def _voltar_menu(self) -> None:
        if self.em_fila:
            self.cliente_rede.sair_fila()
            self.cliente_rede.desconectar()
        self.jogo.voltar_tela()

    def processar_evento(self, evento: pygame.event.Event) -> None:
        if self.modal_ativo and self.modal_ativo.ativo:
            self.modal_ativo.processar_evento(evento)
            return
        self.campo_servidor.processar_evento(evento)
        for btn in self.botoes:
            btn.processar_evento(evento)

    def atualizar(self, dt: float) -> None:
        if self.modal_ativo and self.modal_ativo.ativo:
            self.modal_ativo.atualizar(dt)
        if self.toast_ativo and self.toast_ativo.ativo:
            self.toast_ativo.atualizar(dt)
        self.campo_servidor.atualizar(dt)
        if self.em_fila:
            self.tempo_busca += dt
        self._processar_eventos_rede()

    def _processar_eventos_rede(self) -> None:
        from backend.models.tabuleiro import Tabuleiro
        evento = self.cliente_rede.obter_evento()
        while evento is not None:
            tipo = evento.get('tipo')
            payload = evento.get('payload', {})
            if tipo == 'CONECTADO':
                self.cliente_rede.entrar_fila()
                self.toast_ativo = Toast('Conectado! Buscando oponente...', tipo='INFO')
            elif tipo == TipoMensagem.PARTIDA_ENCONTRADA.value:
                oponente = payload.get('oponente_nome', 'Adversário')
                tempo = payload.get('tempo_segundos', 10)
                self._abrir_modal_match(oponente, tempo)
            elif tipo == TipoMensagem.PARTIDA_CANCELADA.value:
                motivo = payload.get('motivo', 'Partida cancelada.')
                self.modal_ativo = None
                self.som.tocar_som('SoundMessageWarning')
                self.toast_ativo = Toast(motivo, tipo='AVISO')
                self.em_fila = False
                self.btn_entrar_fila.texto = 'BUSCAR PARTIDA (MATCHMAKING)'
                self.btn_entrar_fila.cor_base = COR_PRIMARIA
            elif tipo == TipoMensagem.PARTIDA_INICIADA.value:
                self.modal_ativo = None
                self.em_fila = False
                oponente = payload.get('oponente_nome', 'Adversário')
                self.som.tocar_som('SoundMessageSuccess')
                self.jogo.mudar_tela('posicionamento', modo_jogo=ModoJogo.JOGADOR_VS_JOGADOR_REDE, cliente_rede=self.cliente_rede, oponente_nome=oponente)
                return
            elif tipo == TipoMensagem.ERRO.value:
                msg = payload.get('mensagem', 'Erro de conexão.')
                self.toast_ativo = Toast(msg, tipo='ERRO')
                self.em_fila = False
                self.modal_ativo = None
                self.btn_entrar_fila.texto = 'BUSCAR PARTIDA (MATCHMAKING)'
                self.btn_entrar_fila.cor_base = COR_PRIMARIA
            evento = self.cliente_rede.obter_evento()

    def _abrir_modal_match(self, oponente_nome: str, tempo_segundos: int) -> None:
        self.som.tocar_som('SoundPressStart')
        self.modal_ativo = Modal(titulo='PARTIDA ENCONTRADA!', mensagem=f'Oponente: {oponente_nome}\nAceite a partida antes que o tempo expire!', tipo='MATCH', texto_confirmar='ACEITAR', texto_cancelar='RECUSAR', tempo_limite_segundos=float(tempo_segundos), on_confirmar=self.cliente_rede.aceitar_partida, on_cancelar=self.cliente_rede.recusar_partida, largura=520, altura=280)

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.fill(COR_FUNDO)
        fonte_tit = self.assets.obter_fonte('titulo', negrito=True)
        txt_tit = fonte_tit.render('BATALHA MULTIPLAYER EM REDE', True, COR_TEXTO_DOURADO)
        superficie.blit(txt_tit, ((LARGURA_TELA - txt_tit.get_width()) // 2, 45))
        fonte_sub = self.assets.obter_fonte('media')
        txt_sub = fonte_sub.render('Conecte-se com jogadores em outros computadores via WebSocket', True, COR_TEXTO_MUTED)
        superficie.blit(txt_sub, ((LARGURA_TELA - txt_sub.get_width()) // 2, 92))
        card_w, card_h = (620, 420)
        card_rect = pygame.Rect((LARGURA_TELA - card_w) // 2, 130, card_w, card_h)
        pygame.draw.rect(superficie, COR_PAINEL, card_rect, border_radius=14)
        pygame.draw.rect(superficie, COR_PAINEL_BORDA, card_rect, width=2, border_radius=14)
        fonte_lbl = self.assets.obter_fonte('media', negrito=True)
        txt_lbl = fonte_lbl.render('Endereço do Servidor WebSocket (Host / IP:Porta):', True, COR_TEXTO_BRANCO)
        superficie.blit(txt_lbl, ((LARGURA_TELA - txt_lbl.get_width()) // 2, 172))
        self.campo_servidor.desenhar(superficie)
        fonte_aviso = self.assets.obter_fonte('pequena')
        txt_av1 = fonte_aviso.render('Nota: Servidores gratuitos na nuvem (Render) entram em repouso por inatividade.', True, COR_TEXTO_MUTED)
        txt_av2 = fonte_aviso.render('A primeira conexão pode levar até 50 segundos para acordar o servidor.', True, (246, 173, 85))
        superficie.blit(txt_av1, ((LARGURA_TELA - txt_av1.get_width()) // 2, 258))
        superficie.blit(txt_av2, ((LARGURA_TELA - txt_av2.get_width()) // 2, 276))
        if self.em_fila:
            minutos = int(self.tempo_busca) // 60
            segundos = int(self.tempo_busca) % 60
            if not self.cliente_rede.conectado:
                if self.tempo_busca >= 4.0:
                    txt_msg = f'Acordando servidor na nuvem... ({minutos:02d}:{segundos:02d})'
                else:
                    txt_msg = f'Conectando ao servidor... ({minutos:02d}:{segundos:02d})'
            else:
                txt_msg = f'Conectado! Procurando adversário... ({minutos:02d}:{segundos:02d})'
            txt_status = fonte_lbl.render(txt_msg, True, COR_TEXTO_DOURADO)
            superficie.blit(txt_status, ((LARGURA_TELA - txt_status.get_width()) // 2, 308))
        for btn in self.botoes:
            btn.desenhar(superficie)
        if self.toast_ativo and self.toast_ativo.ativo:
            self.toast_ativo.desenhar(superficie)
        if self.modal_ativo and self.modal_ativo.ativo:
            self.modal_ativo.desenhar(superficie)
