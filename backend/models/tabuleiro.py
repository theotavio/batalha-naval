from __future__ import annotations
import random
from typing import Any
from backend.constantes import TAMANHO_TABULEIRO, EstadoCelula, ResultadoTiro, TipoNavio, Orientacao, FROTA_PADRAO
from backend.excecoes import JogadaRepetidaErro, NavioSobrepostoErro, NavioForaDoTabuleiroErro, PosicaoInvalidaErro
from backend.models.posicao import Posicao
from backend.models.navio import Navio

class Tabuleiro:

    def __init__(self) -> None:
        self.tamanho = TAMANHO_TABULEIRO
        self.navios: list[Navio] = []
        self.tiros_recebidos: set[Posicao] = set()
        self.grade: list[list[EstadoCelula]] = [[EstadoCelula.VAZIO for _ in range(self.tamanho)] for _ in range(self.tamanho)]

    def limpar(self) -> None:
        self.navios.clear()
        self.tiros_recebidos.clear()
        self.grade = [[EstadoCelula.VAZIO for _ in range(self.tamanho)] for _ in range(self.tamanho)]

    def obter_celula(self, linha: int, coluna: int) -> EstadoCelula:
        if not (0 <= linha < self.tamanho and 0 <= coluna < self.tamanho):
            raise PosicaoInvalidaErro(f'Índices fora do tabuleiro: ({linha}, {coluna})')
        return self.grade[linha][coluna]

    def obter_navio_na_posicao(self, posicao: Posicao) -> Navio | None:
        for navio in self.navios:
            if navio.contem_posicao(posicao):
                return navio
        return None

    def pode_posicionar(self, tipo: TipoNavio, posicao_inicial: Posicao, orientacao: Orientacao, ignorar_navio: Navio | None=None) -> bool:
        try:
            temp_navio = Navio(tipo, posicao_inicial, orientacao)
        except NavioForaDoTabuleiroErro:
            return False
        for navio_existente in self.navios:
            if navio_existente is ignorar_navio:
                continue
            if temp_navio.sobrepoe(navio_existente):
                return False
        return True

    def adicionar_navio(self, navio: Navio) -> None:
        for navio_existente in self.navios:
            if navio.sobrepoe(navio_existente):
                raise NavioSobrepostoErro(f'Posicionamento inválido: o navio sobrepõe outro navio existente.')
        self.navios.append(navio)
        for pos in navio.posicoes:
            self.grade[pos.linha][pos.coluna] = EstadoCelula.NAVIO

    def remover_navio(self, navio: Navio) -> None:
        if navio in self.navios:
            self.navios.remove(navio)
            for pos in navio.posicoes:
                self.grade[pos.linha][pos.coluna] = EstadoCelula.VAZIO

    def posicionar_automaticamente(self, frota: tuple[TipoNavio, ...]=FROTA_PADRAO, seed: int | None=None) -> None:
        self.limpar()
        rng = random.Random(seed)
        for tipo in frota:
            posicionado = False
            tentativas = 0
            while not posicionado and tentativas < 1000:
                tentativas += 1
                orientacao = rng.choice([Orientacao.HORIZONTAL, Orientacao.VERTICAL])
                if orientacao == Orientacao.HORIZONTAL:
                    max_linha = self.tamanho - 1
                    max_coluna = self.tamanho - tipo.tamanho
                else:
                    max_linha = self.tamanho - tipo.tamanho
                    max_coluna = self.tamanho - 1
                linha = rng.randint(0, max_linha)
                coluna = rng.randint(0, max_coluna)
                pos = Posicao(linha, coluna)
                if self.pode_posicionar(tipo, pos, orientacao):
                    sprite_id = rng.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
                    navio = Navio(tipo, pos, orientacao, sprite_id=sprite_id)
                    self.adicionar_navio(navio)
                    posicionado = True

    def posicionar_estrategicamente(self, frota: tuple[TipoNavio, ...]=FROTA_PADRAO, seed: int | None=None) -> None:
        self.limpar()
        rng = random.Random(seed)
        navios_ordenados = sorted(frota, key=lambda t: t.tamanho, reverse=True)
        for tipo in navios_ordenados:
            posicionado = False
            tentativas = 0
            while not posicionado and tentativas < 1200:
                tentativas += 1
                orientacao = rng.choice([Orientacao.HORIZONTAL, Orientacao.VERTICAL])
                if tipo == TipoNavio.GRANDE and tentativas < 600:
                    if orientacao == Orientacao.HORIZONTAL:
                        linha = rng.choice([0, 1, self.tamanho - 2, self.tamanho - 1])
                        coluna = rng.randint(0, self.tamanho - tipo.tamanho)
                    else:
                        linha = rng.randint(0, self.tamanho - tipo.tamanho)
                        coluna = rng.choice([0, 1, self.tamanho - 2, self.tamanho - 1])
                elif orientacao == Orientacao.HORIZONTAL:
                    linha = rng.randint(0, self.tamanho - 1)
                    coluna = rng.randint(0, self.tamanho - tipo.tamanho)
                else:
                    linha = rng.randint(0, self.tamanho - tipo.tamanho)
                    coluna = rng.randint(0, self.tamanho - 1)
                pos = Posicao(linha, coluna)
                if self.pode_posicionar(tipo, pos, orientacao):
                    temp_navio = Navio(tipo, pos, orientacao)
                    isolado = True
                    if tentativas < 800:
                        for n_existente in self.navios:
                            for p_novo in temp_navio.posicoes:
                                for p_exist in n_existente.posicoes:
                                    if abs(p_novo.linha - p_exist.linha) <= 1 and abs(p_novo.coluna - p_exist.coluna) <= 1:
                                        isolado = False
                                        break
                                if not isolado:
                                    break
                            if not isolado:
                                break
                    if isolado:
                        sprite_id = rng.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
                        navio = Navio(tipo, pos, orientacao, sprite_id=sprite_id)
                        self.adicionar_navio(navio)
                        posicionado = True
        if len(self.navios) < len(frota):
            self.posicionar_automaticamente(frota=frota, seed=seed)

    def foi_atacada(self, posicao: Posicao) -> bool:
        return posicao in self.tiros_recebidos

    def processar_tiro(self, posicao: Posicao) -> tuple[ResultadoTiro, Navio | None]:
        if self.foi_atacada(posicao):
            raise JogadaRepetidaErro(f'A coordenada {posicao.para_coordenada()} já foi atacada anteriormente! Escolha outra.')
        self.tiros_recebidos.add(posicao)
        navio_atingido = self.obter_navio_na_posicao(posicao)
        if navio_atingido is not None:
            navio_atingido.atingir(posicao)
            if navio_atingido.esta_afundado():
                for pos in navio_atingido.posicoes:
                    self.grade[pos.linha][pos.coluna] = EstadoCelula.AFUNDADO
                return (ResultadoTiro.AFUNDADO, navio_atingido)
            else:
                self.grade[posicao.linha][posicao.coluna] = EstadoCelula.ACERTO
                return (ResultadoTiro.ACERTO, navio_atingido)
        else:
            self.grade[posicao.linha][posicao.coluna] = EstadoCelula.AGUA
            return (ResultadoTiro.AGUA, None)

    def todos_navios_afundados(self) -> bool:
        if not self.navios:
            return False
        return all((navio.esta_afundado() for navio in self.navios))

    def navios_restantes(self) -> list[Navio]:
        return [navio for navio in self.navios if not navio.esta_afundado()]

    def posicoes_nao_atacadas(self) -> list[Posicao]:
        nao_atacadas: list[Posicao] = []
        for l in range(self.tamanho):
            for c in range(self.tamanho):
                pos = Posicao(l, c)
                if pos not in self.tiros_recebidos:
                    nao_atacadas.append(pos)
        return nao_atacadas

    def para_dict(self) -> dict[str, Any]:
        return {'tamanho': self.tamanho, 'navios': [n.para_dict() for n in self.navios], 'tiros_recebidos': [(p.linha, p.coluna) for p in self.tiros_recebidos]}

    @classmethod
    def de_dict(cls, data: dict[str, Any]) -> Tabuleiro:
        tabuleiro = cls()
        for navio_data in data.get('navios', []):
            navio = Navio.de_dict(navio_data)
            tabuleiro.adicionar_navio(navio)
        for linha, coluna in data.get('tiros_recebidos', []):
            pos = Posicao(linha, coluna)
            tabuleiro.tiros_recebidos.add(pos)
            navio = tabuleiro.obter_navio_na_posicao(pos)
            if navio:
                if navio.esta_afundado():
                    tabuleiro.grade[linha][coluna] = EstadoCelula.AFUNDADO
                else:
                    tabuleiro.grade[linha][coluna] = EstadoCelula.ACERTO
            else:
                tabuleiro.grade[linha][coluna] = EstadoCelula.AGUA
        return tabuleiro
