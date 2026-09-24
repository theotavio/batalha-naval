from __future__ import annotations
import os
import sys
from pathlib import Path
RAIZ_PROJETO = str(Path(__file__).resolve().parent.parent.parent)
if RAIZ_PROJETO not in sys.path:
    sys.path.insert(0, RAIZ_PROJETO)
import asyncio
import json
import uuid
import logging
from typing import Any
import socket
import websockets
from websockets.asyncio.server import ServerConnection
from backend.rede.protocolo import TipoMensagem
import socket
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger('ServidorMatchmaking')
logging.getLogger('websockets.server').setLevel(logging.CRITICAL)
logging.getLogger('websockets.protocol').setLevel(logging.CRITICAL)

def esta_servidor_rodando(host: str='127.0.0.1', porta: int=8765) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.4)
            return s.connect_ex((host, porta)) == 0
    except Exception:
        return False

class JogadorConectado:

    def __init__(self, websocket: ServerConnection, nome: str) -> None:
        self.websocket = websocket
        self.id = str(uuid.uuid4())[:8]
        self.nome = nome
        self.em_fila: bool = False
        self.aceitou: bool = False
        self.partida_id: str | None = None
        self.frota_enviada: dict[str, Any] | None = None

class SalaPartida:

    def __init__(self, id_sala: str, jogador1: JogadorConectado, jogador2: JogadorConectado) -> None:
        self.id_sala = id_sala
        self.jogador1 = jogador1
        self.jogador2 = jogador2
        self.vez_jogador1: bool = True
        self.iniciada: bool = False

    def oponente_de(self, jogador: JogadorConectado) -> JogadorConectado:
        return self.jogador2 if jogador == self.jogador1 else self.jogador1

class ServidorMatchmaking:

    def __init__(self, host: str='0.0.0.0', porta: int=8765) -> None:
        self.host = host
        self.porta = porta
        self.conexoes: dict[ServerConnection, JogadorConectado] = {}
        self.fila_matchmaking: list[JogadorConectado] = []
        self.propostas_partida: dict[str, tuple[JogadorConectado, JogadorConectado, asyncio.Task[None]]] = {}
        self.salas_ativas: dict[str, SalaPartida] = {}
        self._servidor: Any = None

    async def iniciar(self) -> None:
        logger.info(f'Iniciando Servidor de Matchmaking em {self.host}:{self.porta}...')
        self._servidor = await websockets.serve(self._gerenciar_conexao, self.host, self.porta)
        logger.info('Servidor pronto e aguardando jogadores!')

    async def parar(self) -> None:
        if self._servidor:
            self._servidor.close()
            await self._servidor.wait_closed()
            logger.info('Servidor encerrado.')

    async def _enviar(self, jogador: JogadorConectado, tipo: TipoMensagem, payload: dict[str, Any]) -> None:
        try:
            msg = json.dumps({'tipo': tipo.value, 'payload': payload})
            await jogador.websocket.send(msg)
        except Exception as e:
            logger.warning(f'Erro ao enviar para {jogador.nome}: {e}')

    async def _gerenciar_conexao(self, websocket: ServerConnection) -> None:
        jogador = JogadorConectado(websocket, nome='Jogador Anônimo')
        self.conexoes[websocket] = jogador
        logger.info(f'Novo cliente conectado: {jogador.id}')
        try:
            async for mensagem in websocket:
                try:
                    dados = json.loads(mensagem)
                    tipo = TipoMensagem(dados.get('tipo'))
                    payload = dados.get('payload', {})
                    await self._processar_mensagem(jogador, tipo, payload)
                except Exception as e:
                    logger.error(f'Erro ao processar mensagem do jogador {jogador.nome}: {e}')
        except websockets.ConnectionClosed:
            pass
        finally:
            await self._desconectar_jogador(jogador)

    async def _desconectar_jogador(self, jogador: JogadorConectado) -> None:
        logger.info(f'Jogador desconectado: {jogador.nome} ({jogador.id})')
        if jogador.websocket in self.conexoes:
            del self.conexoes[jogador.websocket]
        if jogador in self.fila_matchmaking:
            self.fila_matchmaking.remove(jogador)
        if jogador.partida_id and jogador.partida_id in self.propostas_partida:
            j1, j2, task = self.propostas_partida.pop(jogador.partida_id)
            task.cancel()
            outro = j2 if jogador == j1 else j1
            outro.partida_id = None
            await self._enviar(outro, TipoMensagem.PARTIDA_CANCELADA, {'motivo': 'O oponente desconectou.'})
        if jogador.partida_id and jogador.partida_id in self.salas_ativas:
            sala = self.salas_ativas.pop(jogador.partida_id)
            oponente = sala.oponente_de(jogador)
            oponente.partida_id = None
            await self._enviar(oponente, TipoMensagem.OPONENTE_DESCONECTOU, {'motivo': 'Oponente desconectou.'})

    async def _processar_mensagem(self, jogador: JogadorConectado, tipo: TipoMensagem, payload: dict[str, Any]) -> None:
        if tipo == TipoMensagem.ENTRAR_FILA:
            jogador.nome = payload.get('nome', jogador.nome)
            if jogador not in self.fila_matchmaking:
                self.fila_matchmaking.append(jogador)
                jogador.em_fila = True
                logger.info(f'{jogador.nome} entrou na fila. Total na fila: {len(self.fila_matchmaking)}')
                await self._verificar_matchmaking()
        elif tipo == TipoMensagem.SAIR_FILA:
            if jogador in self.fila_matchmaking:
                self.fila_matchmaking.remove(jogador)
                jogador.em_fila = False
                logger.info(f'{jogador.nome} saiu da fila.')
        elif tipo == TipoMensagem.ACEITAR_PARTIDA:
            partida_id = payload.get('partida_id')
            if partida_id in self.propostas_partida:
                jogador.aceitou = True
                j1, j2, _ = self.propostas_partida[partida_id]
                if j1.aceitou and j2.aceitou:
                    await self._iniciar_sala_jogo(partida_id)
        elif tipo == TipoMensagem.RECUSAR_PARTIDA:
            partida_id = payload.get('partida_id')
            if partida_id in self.propostas_partida:
                j1, j2, task = self.propostas_partida.pop(partida_id)
                task.cancel()
                outro = j2 if jogador == j1 else j1
                jogador.partida_id = None
                outro.partida_id = None
                if outro not in self.fila_matchmaking:
                    self.fila_matchmaking.insert(0, outro)
                await self._enviar(outro, TipoMensagem.PARTIDA_CANCELADA, {'motivo': 'O oponente recusou a partida.'})
                await self._enviar(jogador, TipoMensagem.PARTIDA_CANCELADA, {'motivo': 'Você recusou a partida.'})
        elif tipo == TipoMensagem.ENVIAR_FROTA:
            partida_id = jogador.partida_id
            if partida_id and partida_id in self.salas_ativas:
                sala = self.salas_ativas[partida_id]
                jogador.frota_enviada = payload.get('tabuleiro')
                oponente = sala.oponente_de(jogador)
                if sala.jogador1.frota_enviada and sala.jogador2.frota_enviada:
                    sala.iniciada = True
                    await self._enviar(sala.jogador1, TipoMensagem.FROTAS_CONFIRMADAS, {'sua_vez': True, 'oponente_nome': sala.jogador2.nome, 'oponente_frota': sala.jogador2.frota_enviada})
                    await self._enviar(sala.jogador2, TipoMensagem.FROTAS_CONFIRMADAS, {'sua_vez': False, 'oponente_nome': sala.jogador1.nome, 'oponente_frota': sala.jogador1.frota_enviada})
        elif tipo == TipoMensagem.DISPARAR_TIRO:
            partida_id = jogador.partida_id
            if partida_id and partida_id in self.salas_ativas:
                sala = self.salas_ativas[partida_id]
                oponente = sala.oponente_de(jogador)
                await self._enviar(oponente, TipoMensagem.DISPARAR_TIRO, payload)
        elif tipo == TipoMensagem.RESULTADO_TIRO:
            partida_id = jogador.partida_id
            if partida_id and partida_id in self.salas_ativas:
                sala = self.salas_ativas[partida_id]
                oponente = sala.oponente_de(jogador)
                await self._enviar(oponente, TipoMensagem.RESULTADO_TIRO, payload)

    async def _verificar_matchmaking(self) -> None:
        while len(self.fila_matchmaking) >= 2:
            j1 = self.fila_matchmaking.pop(0)
            j2 = self.fila_matchmaking.pop(0)
            j1.em_fila = False
            j2.em_fila = False
            partida_id = str(uuid.uuid4())[:8]
            j1.partida_id = partida_id
            j2.partida_id = partida_id
            j1.aceitou = False
            j2.aceitou = False
            task = asyncio.create_task(self._timeout_aceite(partida_id))
            self.propostas_partida[partida_id] = (j1, j2, task)
            tempo_aceite = 10
            await self._enviar(j1, TipoMensagem.PARTIDA_ENCONTRADA, {'partida_id': partida_id, 'oponente_nome': j2.nome, 'tempo_segundos': tempo_aceite})
            await self._enviar(j2, TipoMensagem.PARTIDA_ENCONTRADA, {'partida_id': partida_id, 'oponente_nome': j1.nome, 'tempo_segundos': tempo_aceite})

    async def _timeout_aceite(self, partida_id: str) -> None:
        try:
            await asyncio.sleep(10.5)
            if partida_id in self.propostas_partida:
                j1, j2, _ = self.propostas_partida.pop(partida_id)
                j1.partida_id = None
                j2.partida_id = None
                if j1.aceitou and (not j2.aceitou):
                    self.fila_matchmaking.insert(0, j1)
                    await self._enviar(j1, TipoMensagem.PARTIDA_CANCELADA, {'motivo': 'Oponente não aceitou a tempo.'})
                    await self._enviar(j2, TipoMensagem.PARTIDA_CANCELADA, {'motivo': 'Você não aceitou a tempo.'})
                elif j2.aceitou and (not j1.aceitou):
                    self.fila_matchmaking.insert(0, j2)
                    await self._enviar(j2, TipoMensagem.PARTIDA_CANCELADA, {'motivo': 'Oponente não aceitou a tempo.'})
                    await self._enviar(j1, TipoMensagem.PARTIDA_CANCELADA, {'motivo': 'Você não aceitou a tempo.'})
                else:
                    await self._enviar(j1, TipoMensagem.PARTIDA_CANCELADA, {'motivo': 'Partida expirada.'})
                    await self._enviar(j2, TipoMensagem.PARTIDA_CANCELADA, {'motivo': 'Partida expirada.'})
        except asyncio.CancelledError:
            pass

    async def _iniciar_sala_jogo(self, partida_id: str) -> None:
        if partida_id not in self.propostas_partida:
            return
        j1, j2, task = self.propostas_partida.pop(partida_id)
        task.cancel()
        sala = SalaPartida(partida_id, j1, j2)
        self.salas_ativas[partida_id] = sala
        logger.info(f'Partida iniciada entre {j1.nome} e {j2.nome} (Sala {partida_id})')
        await self._enviar(j1, TipoMensagem.PARTIDA_INICIADA, {'partida_id': partida_id, 'oponente_nome': j2.nome})
        await self._enviar(j2, TipoMensagem.PARTIDA_INICIADA, {'partida_id': partida_id, 'oponente_nome': j1.nome})

async def executar_servidor(host: str='0.0.0.0', porta: int=8765) -> None:
    servidor = ServidorMatchmaking(host, porta)
    await servidor.iniciar()
    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        await servidor.parar()
if __name__ == '__main__':
    import os
    porta_env = int(os.environ.get('PORT', '8765'))
    asyncio.run(executar_servidor(porta=porta_env))
