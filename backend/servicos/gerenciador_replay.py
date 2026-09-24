from __future__ import annotations
from typing import Any
from backend.constantes import ResultadoTiro, EstadoCelula
from backend.models.posicao import Posicao
from backend.models.tabuleiro import Tabuleiro
from backend.models.jogada import Jogada

class GerenciadorReplay:

    def __init__(self) -> None:
        self.dados_replay: dict[str, Any] | None = None
        self.tabuleiro1 = Tabuleiro()
        self.tabuleiro2 = Tabuleiro()
        self.jogador1_nome: str = 'Jogador 1'
        self.jogador2_nome: str = 'Jogador 2'
        self.jogadas: list[Jogada] = []
        self.indice_atual: int = 0
        self.em_reproducao: bool = False
        self.velocidade: float = 1.0
        self._acumulador_tempo: float = 0.0
        self._intervalo_base: float = 1.0

    def carregar_replay(self, dados: dict[str, Any]) -> None:
        self.dados_replay = dados
        self.jogador1_nome = dados.get('jogador1_nome', 'Jogador 1')
        self.jogador2_nome = dados.get('jogador2_nome', 'Jogador 2')
        self.jogadas = [Jogada.de_dict(j) for j in dados.get('historico_jogadas', [])]
        self.reiniciar()

    def reiniciar(self) -> None:
        if not self.dados_replay:
            return
        config = self.dados_replay.get('config_inicial', {})
        tab1_data = config.get('jogador1', {}).get('tabuleiro')
        tab2_data = config.get('jogador2', {}).get('tabuleiro')
        if tab1_data:
            self.tabuleiro1 = Tabuleiro.de_dict({'tamanho': 10, 'navios': tab1_data.get('navios', [])})
        else:
            self.tabuleiro1 = Tabuleiro()
        if tab2_data:
            self.tabuleiro2 = Tabuleiro.de_dict({'tamanho': 10, 'navios': tab2_data.get('navios', [])})
        else:
            self.tabuleiro2 = Tabuleiro()
        self.indice_atual = 0
        self.em_reproducao = False
        self._acumulador_tempo = 0.0

    @property
    def total_jogadas(self) -> int:
        return len(self.jogadas)

    @property
    def finalizado(self) -> bool:
        return self.indice_atual >= len(self.jogadas)

    def avancar_passo(self) -> Jogada | None:
        if self.finalizado:
            self.em_reproducao = False
            return None
        jogada = self.jogadas[self.indice_atual]
        if jogada.jogador_nome == self.jogador1_nome:
            self.tabuleiro2.processar_tiro(jogada.posicao)
        else:
            self.tabuleiro1.processar_tiro(jogada.posicao)
        self.indice_atual += 1
        if self.finalizado:
            self.em_reproducao = False
        return jogada

    def voltar_passo(self) -> None:
        if self.indice_atual <= 0:
            return
        alvo = self.indice_atual - 1
        self.ir_para_jogada(alvo)

    def ir_para_jogada(self, indice_alvo: int) -> None:
        alvo = max(0, min(indice_alvo, len(self.jogadas)))
        self.reiniciar()
        for _ in range(alvo):
            self.avancar_passo()

    def alternar_play_pause(self) -> bool:
        if self.finalizado and (not self.em_reproducao):
            self.reiniciar()
        self.em_reproducao = not self.em_reproducao
        return self.em_reproducao

    def alternar_velocidade(self) -> float:
        if self.velocidade == 1.0:
            self.velocidade = 2.0
        elif self.velocidade == 2.0:
            self.velocidade = 4.0
        else:
            self.velocidade = 1.0
        return self.velocidade

    def atualizar(self, delta_tempo: float) -> Jogada | None:
        if not self.em_reproducao or self.finalizado:
            return None
        self._acumulador_tempo += delta_tempo
        intervalo_ajustado = self._intervalo_base / self.velocidade
        if self._acumulador_tempo >= intervalo_ajustado:
            self._acumulador_tempo = 0.0
            return self.avancar_passo()
        return None
