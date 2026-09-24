from __future__ import annotations
import time
from typing import Callable, Any
import pygame
from frontend.core.constantes import LARGURA_TELA, ALTURA_TELA, COR_PAINEL, COR_PAINEL_BORDA, COR_PAINEL_GLOW, COR_PRIMARIA, COR_SECUNDARIA, COR_SUCESSO, COR_PERIGO, COR_TEXTO_BRANCO, COR_TEXTO_MUTED
from frontend.core.gerenciador_assets import GerenciadorAssets
from frontend.core.gerenciador_som import GerenciadorSom
from frontend.componentes.botao import Botao

class Modal:

    def __init__(self, titulo: str, mensagem: str, tipo: str='AVISO', on_confirmar: Callable[[], Any] | None=None, on_cancelar: Callable[[], Any] | None=None, texto_confirmar: str='OK', texto_cancelar: str='Cancelar', tempo_limite_segundos: float | None=None, largura: int=540, altura: int=300) -> None:
        self.titulo = titulo
        self.mensagem = mensagem
        self.tipo = tipo
        self.on_confirmar = on_confirmar
        self.on_cancelar = on_cancelar
        self.tempo_limite_segundos = tempo_limite_segundos
        self.tempo_inicio = time.time()
        self.ativo: bool = True
        assets = GerenciadorAssets.obter_instancia()
        fonte_msg = assets.obter_fonte('media')
        largura_maxima_texto = largura - 50
        self.linhas_processadas: list[str] = []
        for bloco in mensagem.split('\n'):
            if not bloco.strip():
                self.linhas_processadas.append('')
                continue
            palavras = bloco.split(' ')
            linha_atual = ''
            for p in palavras:
                teste = f'{linha_atual} {p}'.strip() if linha_atual else p
                if fonte_msg.size(teste)[0] <= largura_maxima_texto:
                    linha_atual = teste
                else:
                    if linha_atual:
                        self.linhas_processadas.append(linha_atual)
                    linha_atual = p
            if linha_atual:
                self.linhas_processadas.append(linha_atual)
        altura_calculada = max(altura, 140 + len(self.linhas_processadas) * 26 + (36 if tempo_limite_segundos else 0))
        self.largura = largura
        self.altura = altura_calculada
        self.x = (LARGURA_TELA - largura) // 2
        self.y = (ALTURA_TELA - altura_calculada) // 2
        self.rect = pygame.Rect(self.x, self.y, self.largura, self.altura)
        self.botoes: list[Botao] = []
        self._criar_botoes(texto_confirmar, texto_cancelar)
        som = GerenciadorSom.obter_instancia()
        if tipo == 'ERRO':
            som.tocar_som('SoundMessageError')
        elif tipo == 'MATCH':
            som.tocar_som('SoundPressStart')
        elif tipo == 'CONFIRMACAO':
            som.tocar_som('SoundAreYouSure')
        else:
            som.tocar_som('SoundMessageWarning')

    def _criar_botoes(self, texto_conf: str, texto_canc: str) -> None:
        btn_h = 42
        btn_y = self.rect.bottom - btn_h - 18
        if self.tipo in ('CONFIRMACAO', 'MATCH'):
            btn_w = (self.largura - 56) // 2
            btn_conf = Botao((self.rect.x + 20, btn_y, btn_w, btn_h), texto=texto_conf, on_click=self._acao_confirmar, cor_base=COR_SUCESSO, cor_hover=(52, 211, 153), tamanho_fonte='media')
            btn_canc = Botao((self.rect.x + 36 + btn_w, btn_y, btn_w, btn_h), texto=texto_canc, on_click=self._acao_cancelar, cor_base=COR_PERIGO, cor_hover=(248, 113, 113), tamanho_fonte='media')
            self.botoes.extend([btn_conf, btn_canc])
        else:
            btn_w = 180
            btn_ok = Botao(((LARGURA_TELA - btn_w) // 2, btn_y, btn_w, btn_h), texto=texto_conf, on_click=self._acao_confirmar, cor_base=COR_PRIMARIA, cor_hover=COR_PAINEL_GLOW, tamanho_fonte='media')
            self.botoes.append(btn_ok)

    def _acao_confirmar(self) -> None:
        self.ativo = False
        if self.on_confirmar:
            self.on_confirmar()

    def _acao_cancelar(self) -> None:
        self.ativo = False
        if self.on_cancelar:
            self.on_cancelar()

    def processar_evento(self, evento: pygame.event.Event) -> bool:
        if not self.ativo:
            return False
        for btn in self.botoes:
            if btn.processar_evento(evento):
                return True
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self._acao_cancelar()
            return True
        if evento.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            return True
        return False

    def atualizar(self, dt: float) -> None:
        if not self.ativo:
            return
        if self.tempo_limite_segundos is not None:
            decorrido = time.time() - self.tempo_inicio
            if decorrido >= self.tempo_limite_segundos:
                self._acao_cancelar()

    def desenhar(self, superficie: pygame.Surface) -> None:
        if not self.ativo:
            return
        assets = GerenciadorAssets.obter_instancia()
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        superficie.blit(overlay, (0, 0))
        sombra = pygame.Rect(self.rect.x, self.rect.y + 4, self.rect.width, self.rect.height)
        sombra_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(sombra_surf, (0, 0, 0, 140), sombra_surf.get_rect(), border_radius=14)
        superficie.blit(sombra_surf, sombra)
        cor_borda = COR_PERIGO if self.tipo == 'ERRO' else COR_SECUNDARIA if self.tipo == 'MATCH' else COR_PAINEL_GLOW
        pygame.draw.rect(superficie, COR_PAINEL, self.rect, border_radius=14)
        pygame.draw.rect(superficie, cor_borda, self.rect, width=2, border_radius=14)
        fonte_titulo = assets.obter_fonte('grande', negrito=True)
        txt_titulo = fonte_titulo.render(self.titulo, True, COR_TEXTO_BRANCO)
        superficie.blit(txt_titulo, (self.rect.x + 24, self.rect.y + 16))
        pygame.draw.line(superficie, COR_PAINEL_BORDA, (self.rect.x + 20, self.rect.y + 52), (self.rect.right - 20, self.rect.y + 52), 1)
        fonte_msg = assets.obter_fonte('media')
        curr_y = self.rect.y + 64
        for linha in self.linhas_processadas:
            if linha:
                txt_msg = fonte_msg.render(linha, True, COR_TEXTO_MUTED)
                superficie.blit(txt_msg, (self.rect.x + 24, curr_y))
            curr_y += 24
        if self.tempo_limite_segundos is not None and self.tipo == 'MATCH':
            decorrido = time.time() - self.tempo_inicio
            restante = max(0.0, self.tempo_limite_segundos - decorrido)
            progresso = restante / self.tempo_limite_segundos
            barra_x = self.rect.x + 24
            barra_y = curr_y + 8
            barra_w = self.largura - 48
            barra_h = 8
            pygame.draw.rect(superficie, (40, 50, 65), (barra_x, barra_y, barra_w, barra_h), border_radius=4)
            largura_atual = int(barra_w * progresso)
            if largura_atual > 0:
                pygame.draw.rect(superficie, COR_SUCESSO, (barra_x, barra_y, largura_atual, barra_h), border_radius=4)
        for btn in self.botoes:
            btn.desenhar(superficie)
