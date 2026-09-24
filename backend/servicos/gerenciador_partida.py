from __future__ import annotations
import time
import random
from typing import Any
from backend.constantes import ModoJogo, DificuldadeIA, EstadoPartida, ResultadoTiro
from backend.excecoes import PartidaFinalizadaErro, FrotaIncompletaErro, JogadaRepetidaErro
from backend.models.posicao import Posicao
from backend.models.navio import Navio
from backend.models.tabuleiro import Tabuleiro
from backend.models.jogada import Jogada
from backend.models.jogador import Jogador, JogadorHumano, JogadorComputador, JogadorRemoto
from backend.database.repositorio import Repositorio

class Partida:

    def __init__(self, jogador1: Jogador, jogador2: Jogador, modo_jogo: ModoJogo=ModoJogo.JOGADOR_VS_COMPUTADOR, dificuldade: DificuldadeIA | None=None, seed: int | None=None, repositorio: Repositorio | None=None) -> None:
        self.jogador1 = jogador1
        self.jogador2 = jogador2
        self.modo_jogo = modo_jogo
        self.dificuldade = dificuldade
        self.seed = seed if seed is not None else random.randint(1, 1000000)
        self.repositorio = repositorio or Repositorio()
        self.estado: EstadoPartida = EstadoPartida.POSICIONAMENTO
        self.turno_atual: int = 1
        self.jogador_da_vez: Jogador = self.jogador1
        self.vencedor: Jogador | None = None
        self.historico_jogadas: list[Jogada] = []
        self.tempo_inicio: float = 0.0
        self.tempo_fim: float = 0.0
        self.tempo_pausado_acumulado: float = 0.0
        self._momento_pausa: float = 0.0
        self._config_inicial: dict[str, Any] = {}

    @property
    def tempo_total_segundos(self) -> int:
        if self.tempo_inicio == 0.0:
            return 0
        if self.estado == EstadoPartida.FINALIZADA:
            fim = self.tempo_fim if self.tempo_fim > 0 else time.time()
            return max(0, int(fim - self.tempo_inicio - self.tempo_pausado_acumulado))
        if self.estado == EstadoPartida.PAUSADA:
            return max(0, int(self._momento_pausa - self.tempo_inicio - self.tempo_pausado_acumulado))
        return max(0, int(time.time() - self.tempo_inicio - self.tempo_pausado_acumulado))

    @property
    def tempo_formatado(self) -> str:
        segundos = self.tempo_total_segundos
        minutos = segundos // 60
        segs = segundos % 60
        return f'{minutos:02d}:{segs:02d}'

    def iniciar_partida(self, primeiro_jogador: Jogador | None=None) -> None:
        if not self.jogador1.tabuleiro.navios or not self.jogador2.tabuleiro.navios:
            raise FrotaIncompletaErro('Ambos os jogadores devem posicionar todos os navios antes de iniciar!')
        self._config_inicial = {'seed': self.seed, 'jogador1': {'nome': self.jogador1.nome, 'tabuleiro': self.jogador1.tabuleiro.para_dict()}, 'jogador2': {'nome': self.jogador2.nome, 'tabuleiro': self.jogador2.tabuleiro.para_dict()}}
        self.estado = EstadoPartida.EM_ANDAMENTO
        self.tempo_inicio = time.time()
        self.turno_atual = 1
        self.jogador_da_vez = primeiro_jogador or self.jogador_da_vez or self.jogador1

    def pausar(self) -> None:
        if self.estado == EstadoPartida.EM_ANDAMENTO:
            self.estado = EstadoPartida.PAUSADA
            self._momento_pausa = time.time()

    def despausar(self) -> None:
        if self.estado == EstadoPartida.PAUSADA:
            self.tempo_pausado_acumulado += time.time() - self._momento_pausa
            self.estado = EstadoPartida.EM_ANDAMENTO

    def obter_jogador_adversario(self, jogador: Jogador) -> Jogador:
        return self.jogador2 if jogador is self.jogador1 else self.jogador1

    def executar_jogada(self, posicao: Posicao, atacante: Jogador | None=None) -> Jogada:
        if self.estado != EstadoPartida.EM_ANDAMENTO:
            raise PartidaFinalizadaErro('A partida não está em andamento.')
        atacante_efetivo = atacante if atacante is not None else self.jogador_da_vez
        defensor = self.obter_jogador_adversario(atacante_efetivo)
        resultado, navio_atingido = defensor.tabuleiro.processar_tiro(posicao)
        atacante_efetivo.registrar_resultado_tiro(resultado)
        tipo_navio = navio_atingido.tipo if navio_atingido else None
        navio_afundado = navio_atingido.esta_afundado() if navio_atingido else False
        jogada = Jogada(numero_turno=self.turno_atual, jogador_nome=atacante_efetivo.nome, posicao=posicao, resultado=resultado, tipo_navio=tipo_navio, navio_afundado=navio_afundado, timestamp=time.time())
        self.historico_jogadas.append(jogada)
        if isinstance(atacante_efetivo, JogadorComputador):
            atacante_efetivo.registrar_feedback_ia(posicao, resultado, navio_atingido if navio_afundado else None)
        if defensor.tabuleiro.todos_navios_afundados():
            self._finalizar_partida(vencedor=atacante_efetivo)
        else:
            self.jogador_da_vez = self.obter_jogador_adversario(atacante_efetivo)
            if self.jogador_da_vez is self.jogador1:
                self.turno_atual += 1
            for jogador in (self.jogador1, self.jogador2):
                if isinstance(jogador, JogadorComputador):
                    if hasattr(jogador.ia, 'reposicionar_frota_propria'):
                        jogador.ia.reposicionar_frota_propria(jogador.tabuleiro)
        return jogada

    def _finalizar_partida(self, vencedor: Jogador) -> None:
        self.estado = EstadoPartida.FINALIZADA
        self.tempo_fim = time.time()
        self.vencedor = vencedor
        try:
            jogador1_id = int(self.jogador1.id_jogador) if str(self.jogador1.id_jogador).isdigit() else 1
            j1_venceu = vencedor is self.jogador1
            dificuldade_str = self.dificuldade.value if self.dificuldade else None
            historico_dicts = [j.para_dict() for j in self.historico_jogadas]
            self.repositorio.salvar_partida_e_replay(jogador1_id=jogador1_id, jogador1_nome=self.jogador1.nome, jogador2_nome=self.jogador2.nome, modo_jogo=self.modo_jogo.value, dificuldade=dificuldade_str, vencedor_nome=vencedor.nome, total_jogadas=len(self.historico_jogadas), tempo_segundos=self.tempo_total_segundos, acertos_j1=self.jogador1.total_acertos, erros_j1=self.jogador1.total_erros, maior_seq_j1=self.jogador1.maior_sequencia_acertos, j1_venceu=j1_venceu, seed=self.seed, config_inicial=self._config_inicial, historico_jogadas=historico_dicts)
        except Exception as e:
            print(f'[Aviso] Falha ao persistir partida no banco: {e}')

    def obter_resumo_fim_jogo(self) -> dict[str, Any]:
        vencedor_nome = self.vencedor.nome if self.vencedor else 'Indefinido'
        return {'vencedor': vencedor_nome, 'total_jogadas': len(self.historico_jogadas), 'tempo_formatado': self.tempo_formatado, 'tempo_segundos': self.tempo_total_segundos, 'j1_nome': self.jogador1.nome, 'j1_acertos': self.jogador1.total_acertos, 'j1_erros': self.jogador1.total_erros, 'j1_aproveitamento': round(self.jogador1.aproveitamento, 1), 'j2_nome': self.jogador2.nome, 'j2_acertos': self.jogador2.total_acertos, 'j2_erros': self.jogador2.total_erros, 'j2_aproveitamento': round(self.jogador2.aproveitamento, 1)}
