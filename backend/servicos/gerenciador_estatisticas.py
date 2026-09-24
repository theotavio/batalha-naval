from __future__ import annotations
from typing import Any
from backend.database.repositorio import Repositorio

class GerenciadorEstatisticas:

    def __init__(self, repositorio: Repositorio | None=None) -> None:
        self.repositorio = repositorio or Repositorio()

    def obter_estatisticas(self, jogador_id: int) -> dict[str, Any]:
        return self.repositorio.obter_estatisticas_jogador(jogador_id)

    def obter_taxa_vitorias(self, estatisticas: dict[str, Any]) -> float:
        partidas = estatisticas.get('partidas_jogadas', 0)
        vitorias = estatisticas.get('vitorias', 0)
        if partidas == 0:
            return 0.0
        return round(vitorias / partidas * 100.0, 1)
