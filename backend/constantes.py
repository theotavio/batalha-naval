from enum import Enum
TAMANHO_TABULEIRO = 10
LETRAS_COLUNAS = tuple('ABCDEFGHIJ')
NUMEROS_LINHAS = tuple(range(1, 11))

class TipoNavio(str, Enum):
    PEQUENO = 'Pequeno'
    GRANDE = 'Grande'

    @property
    def tamanho(self) -> int:
        if self == TipoNavio.PEQUENO:
            return 2
        elif self == TipoNavio.GRANDE:
            return 4
        return 2
FROTA_PADRAO = (TipoNavio.GRANDE, TipoNavio.GRANDE, TipoNavio.PEQUENO, TipoNavio.PEQUENO, TipoNavio.PEQUENO, TipoNavio.PEQUENO)

class Orientacao(str, Enum):
    HORIZONTAL = 'HORIZONTAL'
    VERTICAL = 'VERTICAL'

class EstadoCelula(str, Enum):
    VAZIO = 'VAZIO'
    NAVIO = 'NAVIO'
    AGUA = 'AGUA'
    ACERTO = 'ACERTO'
    AFUNDADO = 'AFUNDADO'

class ResultadoTiro(str, Enum):
    AGUA = 'AGUA'
    ACERTO = 'ACERTO'
    AFUNDADO = 'AFUNDADO'

class ModoJogo(str, Enum):
    JOGADOR_VS_COMPUTADOR = 'JOGADOR_VS_COMPUTADOR'
    JOGADOR_VS_JOGADOR_LOCAL = 'JOGADOR_VS_JOGADOR_LOCAL'
    COMPUTADOR_VS_COMPUTADOR = 'COMPUTADOR_VS_COMPUTADOR'
    JOGADOR_VS_JOGADOR_REDE = 'JOGADOR_VS_JOGADOR_REDE'

class DificuldadeIA(str, Enum):
    FACIL = 'FACIL'
    MEDIA = 'MEDIA'
    DIFICIL = 'DIFICIL'
    IMPOSSIVEL = 'IMPOSSIVEL'

class EstadoPartida(str, Enum):
    POSICIONAMENTO = 'POSICIONAMENTO'
    EM_ANDAMENTO = 'EM_ANDAMENTO'
    FINALIZADA = 'FINALIZADA'
    PAUSADA = 'PAUSADA'
