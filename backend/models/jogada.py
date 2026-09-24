from __future__ import annotations
from dataclasses import dataclass, asdict
import time
from typing import Any
from backend.constantes import ResultadoTiro, TipoNavio
from backend.models.posicao import Posicao

@dataclass
class Jogada:
    numero_turno: int
    jogador_nome: str
    posicao: Posicao
    resultado: ResultadoTiro
    tipo_navio: TipoNavio | None = None
    navio_afundado: bool = False
    timestamp: float = 0.0
    mensagem_feedback: str = ''

    def __post_init__(self) -> None:
        if self.timestamp == 0.0:
            self.timestamp = time.time()
        if not self.mensagem_feedback:
            self.mensagem_feedback = self._gerar_mensagem()

    def _gerar_mensagem(self) -> str:
        coord = self.posicao.para_coordenada()
        if self.resultado == ResultadoTiro.AFUNDADO:
            nome_navio = self.tipo_navio.value if self.tipo_navio else 'Navio'
            return f'ACERTO CRÍTICO em {coord}! {nome_navio} inimigo foi AFUNDADO!'
        elif self.resultado == ResultadoTiro.ACERTO:
            nome_navio = self.tipo_navio.value if self.tipo_navio else 'Navio'
            return f'FOGO! {self.jogador_nome} acertou um {nome_navio} em {coord}!'
        else:
            return f'ÁGUA! {self.jogador_nome} disparou em {coord} e atingiu apenas água.'

    def para_dict(self) -> dict[str, Any]:
        return {'numero_turno': self.numero_turno, 'jogador_nome': self.jogador_nome, 'linha': self.posicao.linha, 'coluna': self.posicao.coluna, 'coordenada': self.posicao.para_coordenada(), 'resultado': self.resultado.value, 'tipo_navio': self.tipo_navio.value if self.tipo_navio else None, 'navio_afundado': self.navio_afundado, 'timestamp': self.timestamp, 'mensagem_feedback': self.mensagem_feedback}

    @classmethod
    def de_dict(cls, data: dict[str, Any]) -> Jogada:
        tipo_navio = TipoNavio(data['tipo_navio']) if data.get('tipo_navio') else None
        posicao = Posicao(linha=data['linha'], coluna=data['coluna'])
        return cls(numero_turno=data['numero_turno'], jogador_nome=data['jogador_nome'], posicao=posicao, resultado=ResultadoTiro(data['resultado']), tipo_navio=tipo_navio, navio_afundado=data.get('navio_afundado', False), timestamp=data.get('timestamp', 0.0), mensagem_feedback=data.get('mensagem_feedback', ''))
