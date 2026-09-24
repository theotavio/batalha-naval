from __future__ import annotations
import os
import sys
from pathlib import Path
RAIZ_PROJETO = str(Path(__file__).resolve().parent.parent.parent)
if RAIZ_PROJETO not in sys.path:
    sys.path.insert(0, RAIZ_PROJETO)
import asyncio
import json
import threading
import queue
from typing import Any
import websockets
from websockets.asyncio.client import ClientConnection
from backend.rede.protocolo import TipoMensagem

class ClienteRede:

    def __init__(self) -> None:
        self.url: str = 'ws://127.0.0.1:8765'
        self.nome_jogador: str = 'Jogador'
        self.conectado: bool = False
        self.partida_id_atual: str | None = None
        self.oponente_nome: str = 'Oponente'
        self._fila_eventos_entrada: queue.Queue[dict[str, Any]] = queue.Queue()
        self._fila_mensagens_saida: asyncio.Queue[str] | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._parar_evento = threading.Event()
        self._ws: ClientConnection | None = None

    def conectar(self, url: str, nome_jogador: str) -> None:
        self.url = url
        self.nome_jogador = nome_jogador
        self._parar_evento.clear()
        self._thread = threading.Thread(target=self._executar_loop_async, daemon=True)
        self._thread.start()

    def _executar_loop_async(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._fila_mensagens_saida = asyncio.Queue()
        try:
            self._loop.run_until_complete(self._gerenciar_conexao())
        except Exception as e:
            self._fila_eventos_entrada.put({'tipo': TipoMensagem.ERRO.value, 'payload': {'mensagem': f'Erro de rede: {e}'}})
        finally:
            self.conectado = False

    async def _gerenciar_conexao(self) -> None:
        try:
            async with websockets.connect(self.url) as ws:
                self._ws = ws
                self.conectado = True
                self._fila_eventos_entrada.put({'tipo': 'CONECTADO', 'payload': {'mensagem': 'Conectado ao servidor de matchmaking!'}})
                tarefa_leitura = asyncio.create_task(self._tarefa_leitura(ws))
                tarefa_escrita = asyncio.create_task(self._tarefa_escrita(ws))
                while not self._parar_evento.is_set():
                    await asyncio.sleep(0.05)
                    if ws.close_code is not None:
                        break
                tarefa_leitura.cancel()
                tarefa_escrita.cancel()
        except Exception as e:
            self._fila_eventos_entrada.put({'tipo': TipoMensagem.ERRO.value, 'payload': {'mensagem': f'Falha na conexão: {e}'}})
        finally:
            self.conectado = False

    async def _tarefa_leitura(self, ws: ClientConnection) -> None:
        try:
            async for mensagem in ws:
                dados = json.loads(mensagem)
                tipo = dados.get('tipo')
                payload = dados.get('payload', {})
                if tipo == TipoMensagem.PARTIDA_ENCONTRADA.value:
                    self.partida_id_atual = payload.get('partida_id')
                    self.oponente_nome = payload.get('oponente_nome', 'Oponente')
                self._fila_eventos_entrada.put(dados)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self._fila_eventos_entrada.put({'tipo': TipoMensagem.ERRO.value, 'payload': {'mensagem': f'Erro ao receber dados: {e}'}})

    async def _tarefa_escrita(self, ws: ClientConnection) -> None:
        try:
            while not self._parar_evento.is_set():
                if self._fila_mensagens_saida is not None:
                    msg = await self._fila_mensagens_saida.get()
                    await ws.send(msg)
                    self._fila_mensagens_saida.task_done()
        except asyncio.CancelledError:
            pass
        except Exception:
            pass

    def enviar_mensagem(self, tipo: TipoMensagem, payload: dict[str, Any]) -> None:
        if self._loop and self._fila_mensagens_saida:
            msg_str = json.dumps({'tipo': tipo.value, 'payload': payload})
            self._loop.call_soon_threadsafe(self._fila_mensagens_saida.put_nowait, msg_str)

    def entrar_fila(self) -> None:
        self.enviar_mensagem(TipoMensagem.ENTRAR_FILA, {'nome': self.nome_jogador})

    def sair_fila(self) -> None:
        self.enviar_mensagem(TipoMensagem.SAIR_FILA, {})

    def aceitar_partida(self) -> None:
        if self.partida_id_atual:
            self.enviar_mensagem(TipoMensagem.ACEITAR_PARTIDA, {'partida_id': self.partida_id_atual})

    def recusar_partida(self) -> None:
        if self.partida_id_atual:
            self.enviar_mensagem(TipoMensagem.RECUSAR_PARTIDA, {'partida_id': self.partida_id_atual})

    def enviar_frota(self, tabuleiro_dict: dict[str, Any]) -> None:
        self.enviar_mensagem(TipoMensagem.ENVIAR_FROTA, {'tabuleiro': tabuleiro_dict})

    def disparar_tiro(self, linha: int, coluna: int) -> None:
        self.enviar_mensagem(TipoMensagem.DISPARAR_TIRO, {'linha': linha, 'coluna': coluna})

    def enviar_resultado_tiro(self, linha: int, coluna: int, resultado: str, tipo_navio: str | None, afundado: bool) -> None:
        self.enviar_mensagem(TipoMensagem.RESULTADO_TIRO, {'linha': linha, 'coluna': coluna, 'resultado': resultado, 'tipo_navio': tipo_navio, 'afundado': afundado})

    def obter_evento(self) -> dict[str, Any] | None:
        try:
            return self._fila_eventos_entrada.get_nowait()
        except queue.Empty:
            return None

    def desconectar(self) -> None:
        self._parar_evento.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self.conectado = False
