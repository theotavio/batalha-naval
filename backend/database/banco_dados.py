from __future__ import annotations
import sqlite3
from pathlib import Path
CAMINHO_BD_PADRAO = Path(__file__).resolve().parent.parent.parent / 'data' / 'batalha_naval.db'

class BancoDados:

    def __init__(self, caminho_bd: Path | str=CAMINHO_BD_PADRAO) -> None:
        self.caminho_bd = Path(caminho_bd)
        self.caminho_bd.parent.mkdir(parents=True, exist_ok=True)
        self.inicializar_banco()

    def obter_conexao(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.caminho_bd)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON;')
        return conn

    def inicializar_banco(self) -> None:
        with self.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute('\n                CREATE TABLE IF NOT EXISTS jogadores (\n                    id INTEGER PRIMARY KEY AUTOINCREMENT,\n                    nome TEXT UNIQUE NOT NULL,\n                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n                );\n            ')
            cursor.execute('\n                CREATE TABLE IF NOT EXISTS estatisticas (\n                    jogador_id INTEGER PRIMARY KEY,\n                    partidas_jogadas INTEGER DEFAULT 0,\n                    vitorias INTEGER DEFAULT 0,\n                    derrotas INTEGER DEFAULT 0,\n                    acertos INTEGER DEFAULT 0,\n                    erros INTEGER DEFAULT 0,\n                    maior_sequencia_acertos INTEGER DEFAULT 0,\n                    menor_jogadas_vitoria INTEGER DEFAULT NULL,\n                    FOREIGN KEY(jogador_id) REFERENCES jogadores(id) ON DELETE CASCADE\n                );\n            ')
            cursor.execute('\n                CREATE TABLE IF NOT EXISTS partidas (\n                    id INTEGER PRIMARY KEY AUTOINCREMENT,\n                    jogador1_id INTEGER,\n                    jogador2_nome TEXT NOT NULL,\n                    modo_jogo TEXT NOT NULL,\n                    dificuldade TEXT,\n                    vencedor_nome TEXT NOT NULL,\n                    total_jogadas INTEGER NOT NULL,\n                    tempo_segundos INTEGER NOT NULL,\n                    data_partida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n                    FOREIGN KEY(jogador1_id) REFERENCES jogadores(id) ON DELETE SET NULL\n                );\n            ')
            cursor.execute('\n                CREATE TABLE IF NOT EXISTS replays (\n                    id INTEGER PRIMARY KEY AUTOINCREMENT,\n                    partida_id INTEGER,\n                    titulo TEXT NOT NULL,\n                    modo_jogo TEXT NOT NULL,\n                    jogador1_nome TEXT NOT NULL,\n                    jogador2_nome TEXT NOT NULL,\n                    vencedor_nome TEXT NOT NULL,\n                    seed INTEGER,\n                    config_inicial_json TEXT NOT NULL,\n                    historico_jogadas_json TEXT NOT NULL,\n                    total_jogadas INTEGER NOT NULL,\n                    duracao_segundos INTEGER NOT NULL,\n                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n                    FOREIGN KEY(partida_id) REFERENCES partidas(id) ON DELETE CASCADE\n                );\n            ')
            conn.commit()

    def apagar_todos_os_dados(self) -> None:
        with self.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute('DROP TABLE IF EXISTS replays;')
            cursor.execute('DROP TABLE IF EXISTS partidas;')
            cursor.execute('DROP TABLE IF EXISTS estatisticas;')
            cursor.execute('DROP TABLE IF EXISTS jogadores;')
            conn.commit()
        self.inicializar_banco()
