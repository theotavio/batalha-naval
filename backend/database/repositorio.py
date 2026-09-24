from __future__ import annotations
import json
from typing import Any
from backend.database.banco_dados import BancoDados

class Repositorio:

    def __init__(self, banco: BancoDados | None=None) -> None:
        self.banco = banco or BancoDados()

    def definir_configuracao(self, chave: str, valor: str) -> None:
        with self.banco.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute('\n                INSERT INTO configuracoes (chave, valor) VALUES (?, ?)\n                ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor\n            ', (chave, str(valor)))
            conn.commit()

    def obter_configuracao(self, chave: str, padrao: str | None=None) -> str | None:
        with self.banco.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT valor FROM configuracoes WHERE chave = ?', (chave,))
            row = cursor.fetchone()
            if row:
                return str(row['valor'])
            return padrao

    def obter_ultimo_jogador(self) -> dict[str, Any] | None:
        with self.banco.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT valor FROM configuracoes WHERE chave = ?', ('ultimo_jogador_id',))
            row = cursor.fetchone()
            if row:
                try:
                    jogador_id = int(row['valor'])
                    cursor.execute('SELECT id, nome, data_criacao FROM jogadores WHERE id = ?', (jogador_id,))
                    jogador_row = cursor.fetchone()
                    if jogador_row:
                        return dict(jogador_row)
                except Exception:
                    pass
            cursor.execute('SELECT id, nome, data_criacao FROM jogadores ORDER BY id DESC LIMIT 1')
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def obter_ou_criar_jogador(self, nome: str) -> dict[str, Any]:
        nome_limpo = nome.strip()
        if not nome_limpo:
            nome_limpo = 'Jogador'
        with self.banco.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, nome, data_criacao FROM jogadores WHERE nome = ?', (nome_limpo,))
            row = cursor.fetchone()
            if row:
                dados = dict(row)
                self.definir_configuracao('ultimo_jogador_id', str(dados['id']))
                return dados
            cursor.execute('INSERT INTO jogadores (nome) VALUES (?)', (nome_limpo,))
            jogador_id = cursor.lastrowid
            cursor.execute('\n                INSERT INTO estatisticas (\n                    jogador_id, partidas_jogadas, vitorias, derrotas,\n                    acertos, erros, maior_sequencia_acertos, menor_jogadas_vitoria\n                ) VALUES (?, 0, 0, 0, 0, 0, 0, NULL)\n                ', (jogador_id,))
            conn.commit()
            self.definir_configuracao('ultimo_jogador_id', str(jogador_id))
            return {'id': jogador_id, 'nome': nome_limpo}

    def listar_jogadores(self) -> list[dict[str, Any]]:
        with self.banco.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, nome, data_criacao FROM jogadores ORDER BY nome ASC')
            return [dict(row) for row in cursor.fetchall()]

    def obter_estatisticas_jogador(self, jogador_id: int) -> dict[str, Any]:
        with self.banco.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute('\n                SELECT\n                    j.nome,\n                    e.partidas_jogadas,\n                    e.vitorias,\n                    e.derrotas,\n                    e.acertos,\n                    e.erros,\n                    e.maior_sequencia_acertos,\n                    e.menor_jogadas_vitoria\n                FROM estatisticas e\n                JOIN jogadores j ON j.id = e.jogador_id\n                WHERE e.jogador_id = ?\n                ', (jogador_id,))
            row = cursor.fetchone()
            if not row:
                return {'nome': 'Jogador', 'partidas_jogadas': 0, 'vitorias': 0, 'derrotas': 0, 'acertos': 0, 'erros': 0, 'aproveitamento': 0.0, 'maior_sequencia_acertos': 0, 'menor_jogadas_vitoria': '-'}
            dados = dict(row)
            total_tiros = dados['acertos'] + dados['erros']
            aproveitamento = dados['acertos'] / total_tiros * 100.0 if total_tiros > 0 else 0.0
            dados['aproveitamento'] = round(aproveitamento, 1)
            if dados['menor_jogadas_vitoria'] is None:
                dados['menor_jogadas_vitoria'] = '-'
            return dados

    def salvar_partida_e_replay(self, jogador1_id: int, jogador1_nome: str, jogador2_nome: str, modo_jogo: str, dificuldade: str | None, vencedor_nome: str, total_jogadas: int, tempo_segundos: int, acertos_j1: int, erros_j1: int, maior_seq_j1: int, j1_venceu: bool, seed: int | None, config_inicial: dict[str, Any], historico_jogadas: list[dict[str, Any]]) -> tuple[int, int]:
        with self.banco.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM jogadores WHERE id = ? OR nome = ?', (jogador1_id, jogador1_nome))
            row = cursor.fetchone()
            if row:
                j1_id = row['id']
            else:
                cursor.execute('INSERT INTO jogadores (nome) VALUES (?)', (jogador1_nome,))
                j1_id = cursor.lastrowid
                cursor.execute('\n                    INSERT INTO estatisticas (\n                        jogador_id, partidas_jogadas, vitorias, derrotas,\n                        acertos, erros, maior_sequencia_acertos, menor_jogadas_vitoria\n                    ) VALUES (?, 0, 0, 0, 0, 0, 0, NULL)\n                    ', (j1_id,))
            cursor.execute('\n                INSERT INTO partidas (\n                    jogador1_id, jogador2_nome, modo_jogo, dificuldade,\n                    vencedor_nome, total_jogadas, tempo_segundos\n                ) VALUES (?, ?, ?, ?, ?, ?, ?)\n                ', (j1_id, jogador2_nome, modo_jogo, dificuldade, vencedor_nome, total_jogadas, tempo_segundos))
            partida_id = cursor.lastrowid
            cursor.execute('\n                SELECT\n                    partidas_jogadas, vitorias, derrotas, acertos, erros,\n                    maior_sequencia_acertos, menor_jogadas_vitoria\n                FROM estatisticas\n                WHERE jogador_id = ?\n                ', (jogador1_id,))
            estat = cursor.fetchone()
            if estat:
                p_jogadas = estat['partidas_jogadas'] + 1
                vitorias = estat['vitorias'] + (1 if j1_venceu else 0)
                derrotas = estat['derrotas'] + (0 if j1_venceu else 1)
                acertos = estat['acertos'] + acertos_j1
                erros = estat['erros'] + erros_j1
                maior_seq = max(estat['maior_sequencia_acertos'], maior_seq_j1)
                menor_jogadas = estat['menor_jogadas_vitoria']
                if j1_venceu:
                    if menor_jogadas is None or total_jogadas < menor_jogadas:
                        menor_jogadas = total_jogadas
                cursor.execute('\n                    UPDATE estatisticas SET\n                        partidas_jogadas = ?,\n                        vitorias = ?,\n                        derrotas = ?,\n                        acertos = ?,\n                        erros = ?,\n                        maior_sequencia_acertos = ?,\n                        menor_jogadas_vitoria = ?\n                    WHERE jogador_id = ?\n                    ', (p_jogadas, vitorias, derrotas, acertos, erros, maior_seq, menor_jogadas, jogador1_id))
            titulo = f'{jogador1_nome} vs {jogador2_nome}'
            config_json = json.dumps(config_inicial)
            historico_json = json.dumps(historico_jogadas)
            cursor.execute('\n                INSERT INTO replays (\n                    partida_id, titulo, modo_jogo, jogador1_nome, jogador2_nome,\n                    vencedor_nome, seed, config_inicial_json, historico_jogadas_json,\n                    total_jogadas, duracao_segundos\n                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\n                ', (partida_id, titulo, modo_jogo, jogador1_nome, jogador2_nome, vencedor_nome, seed, config_json, historico_json, total_jogadas, tempo_segundos))
            replay_id = cursor.lastrowid
            conn.commit()
            return (int(partida_id), int(replay_id))

    def listar_replays(self, limite: int=50) -> list[dict[str, Any]]:
        with self.banco.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute('\n                SELECT\n                    id, partida_id, titulo, modo_jogo, jogador1_nome, jogador2_nome,\n                    vencedor_nome, seed, total_jogadas, duracao_segundos, data_criacao\n                FROM replays\n                ORDER BY id DESC\n                LIMIT ?\n                ', (limite,))
            return [dict(row) for row in cursor.fetchall()]

    def obter_replay(self, replay_id: int) -> dict[str, Any] | None:
        with self.banco.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute('\n                SELECT * FROM replays WHERE id = ?\n                ', (replay_id,))
            row = cursor.fetchone()
            if not row:
                return None
            dados = dict(row)
            dados['config_inicial'] = json.loads(dados['config_inicial_json'])
            dados['historico_jogadas'] = json.loads(dados['historico_jogadas_json'])
            return dados

    def obter_ultimo_replay(self) -> dict[str, Any] | None:
        with self.banco.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute('\n                SELECT * FROM replays ORDER BY id DESC LIMIT 1\n                ')
            row = cursor.fetchone()
            if not row:
                return None
            dados = dict(row)
            dados['config_inicial'] = json.loads(dados['config_inicial_json'])
            dados['historico_jogadas'] = json.loads(dados['historico_jogadas_json'])
            return dados

    def resetar_banco_de_dados(self) -> None:
        self.banco.apagar_todos_os_dados()

    def excluir_replay(self, replay_id: int) -> bool:
        with self.banco.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM replays WHERE id = ?', (replay_id,))
            conn.commit()
            return cursor.rowcount > 0

    def excluir_todos_replays(self) -> int:
        with self.banco.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM replays;')
            conn.commit()
            return cursor.rowcount
