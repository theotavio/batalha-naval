from __future__ import annotations
import os
import xml.etree.ElementTree as ET
from pathlib import Path
import pygame
from frontend.core.constantes import TAMANHO_CELULA, COR_AGUA_GRID, COR_PRIMARIA, COR_SECUNDARIA

class GerenciadorAssets:
    _instancia: GerenciadorAssets | None = None

    def __init__(self) -> None:
        self.raiz_assets = Path(__file__).resolve().parent.parent.parent / 'assets'
        self.sprites: dict[str, pygame.Surface] = {}
        self.sons: dict[str, pygame.mixer.Sound] = {}
        self.fontes: dict[str, pygame.font.Font] = {}
        self.musicas: dict[str, str] = {}
        self._carregar_tudo()

    @classmethod
    def obter_instancia(cls) -> GerenciadorAssets:
        if cls._instancia is None:
            cls._instancia = cls()
        return cls._instancia

    def _carregar_tudo(self) -> None:
        self._carregar_fontes()
        self._carregar_spritesheet()
        self._carregar_efeitos_png()
        self._carregar_sons()
        self._mapear_musicas()

    def _carregar_fontes(self) -> None:
        nomes_fontes = ['dejavusans', 'ubuntu', 'segoeui', 'arial', 'helvetica']
        tamanhos = {'pequena': 13, 'media': 16, 'grande': 22, 'titulo': 32, 'destaque': 44}
        self.fontes = {}
        for chave, tam in tamanhos.items():
            fonte_normal = None
            fonte_bold = None
            for nome in nomes_fontes:
                try:
                    if not fonte_normal:
                        fonte_normal = pygame.font.SysFont(nome, tam, bold=False)
                    if not fonte_bold:
                        fonte_bold = pygame.font.SysFont(nome, tam, bold=True)
                    if fonte_normal and fonte_bold:
                        break
                except Exception:
                    continue
            if not fonte_normal:
                fonte_normal = pygame.font.Font(None, tam)
            if not fonte_bold:
                fonte_bold = pygame.font.Font(None, tam)
                fonte_bold.set_bold(True)
            self.fontes[chave, False] = fonte_normal
            self.fontes[chave, True] = fonte_bold
        self._cache_navios: dict[tuple[int, str, int, int | None, bool], pygame.Surface] = {}

    def _carregar_spritesheet(self) -> None:
        caminho_xml = self.raiz_assets / 'sprites' / 'Spritesheet' / 'shipsMiscellaneous_sheet.xml'
        caminho_img = self.raiz_assets / 'sprites' / 'Spritesheet' / 'shipsMiscellaneous_sheet.png'
        if caminho_xml.exists() and caminho_img.exists():
            try:
                sheet = pygame.image.load(str(caminho_img)).convert_alpha()
                tree = ET.parse(caminho_xml)
                root = tree.getroot()
                for sub in root.findall('SubTexture'):
                    nome = sub.get('name', '')
                    x = int(sub.get('x', 0))
                    y = int(sub.get('y', 0))
                    w = int(sub.get('width', 0))
                    h = int(sub.get('height', 0))
                    if w > 0 and h > 0:
                        rect = pygame.Rect(x, y, w, h)
                        sub_surf = sheet.subsurface(rect)
                        self.sprites[nome] = sub_surf
            except Exception as e:
                print(f'[Aviso] Falha ao carregar spritesheet: {e}')

    def _carregar_efeitos_png(self) -> None:
        pasta_efeitos = self.raiz_assets / 'sprites' / 'PNG' / 'Default size' / 'Effects'
        if pasta_efeitos.exists():
            for arquivo in pasta_efeitos.glob('*.png'):
                try:
                    img = pygame.image.load(str(arquivo)).convert_alpha()
                    self.sprites[arquivo.name] = img
                except Exception:
                    pass
        pasta_navios = self.raiz_assets / 'sprites' / 'PNG' / 'Default size' / 'Ships'
        if pasta_navios.exists():
            for arquivo in pasta_navios.glob('*.png'):
                try:
                    img = pygame.image.load(str(arquivo)).convert_alpha()
                    self.sprites[arquivo.name] = img
                except Exception:
                    pass

    def _carregar_sons(self) -> None:
        if not pygame.mixer.get_init():
            return
        pastas = [self.raiz_assets / 'sons' / 'ui', self.raiz_assets / 'sons' / 'canhoes', self.raiz_assets / 'sons' / 'navios']
        for pasta in pastas:
            if pasta.exists():
                for arq in pasta.glob('*.*'):
                    if arq.suffix.lower() in ['.wav', '.ogg']:
                        try:
                            som = pygame.mixer.Sound(str(arq))
                            self.sons[arq.stem] = som
                        except Exception:
                            pass

    def _mapear_musicas(self) -> None:
        pasta_ui = self.raiz_assets / 'sons' / 'ui'
        if pasta_ui.exists():
            for arq in pasta_ui.glob('*.ogg'):
                self.musicas[arq.stem.lower()] = str(arq)

    def obter_fonte(self, tamanho: str='media', negrito: bool=False) -> pygame.font.Font:
        fonte = self.fontes.get((tamanho, negrito))
        if fonte:
            return fonte
        return self.fontes.get(('media', False), pygame.font.Font(None, 16))

    def obter_sprite(self, nome: str) -> pygame.Surface | None:
        return self.sprites.get(nome)

    def obter_som(self, nome: str) -> pygame.mixer.Sound | None:
        return self.sons.get(nome)

    def obter_navio_surface(self, tipo_tamanho: int, orientacao: str, celula_px: int=TAMANHO_CELULA, sprite_id: int | None=None, afundado: bool=False) -> pygame.Surface:
        chave_cache = (tipo_tamanho, orientacao, celula_px, sprite_id, afundado)
        if chave_cache in self._cache_navios:
            return self._cache_navios[chave_cache]
        largura = celula_px * (tipo_tamanho if orientacao == 'HORIZONTAL' else 1)
        altura = celula_px * (1 if orientacao == 'HORIZONTAL' else tipo_tamanho)
        sprites_vivos = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        sprites_afundados = [19, 20, 21, 22, 23, 24]
        seed_id = sprite_id if sprite_id is not None else 1 if tipo_tamanho == 2 else 5
        if afundado:
            sid = sprites_afundados[seed_id % len(sprites_afundados)]
        else:
            sid = sprites_vivos[seed_id % len(sprites_vivos)]
        nome_sprite = f'ship ({sid}).png'
        surf = pygame.Surface((largura, altura), pygame.SRCALPHA)
        sprite_orig = self.obter_sprite(nome_sprite)
        if sprite_orig:
            if orientacao == 'HORIZONTAL':
                sprite_rot = pygame.transform.rotate(sprite_orig, -90)
                sprite_redim = pygame.transform.smoothscale(sprite_rot, (largura - 4, altura - 4))
            else:
                sprite_redim = pygame.transform.smoothscale(sprite_orig, (largura - 4, altura - 4))
            sombra = pygame.Surface((largura - 4, altura - 4), pygame.SRCALPHA)
            sombra.fill((0, 0, 0, 90 if afundado else 60))
            surf.blit(sombra, (3, 3))
            surf.blit(sprite_redim, (2, 2))
            if afundado:
                dano_overlay = pygame.Surface((largura - 4, altura - 4), pygame.SRCALPHA)
                dano_overlay.fill((180, 20, 20, 55))
                surf.blit(dano_overlay, (2, 2))
        else:
            rect = pygame.Rect(2, 2, largura - 4, altura - 4)
            cor = (40, 45, 55) if afundado else COR_PRIMARIA if tipo_tamanho == 2 else COR_SECUNDARIA
            pygame.draw.rect(surf, cor, rect, border_radius=6)
            pygame.draw.rect(surf, (200, 50, 50) if afundado else (255, 255, 255), rect, width=2, border_radius=6)
        self._cache_navios[chave_cache] = surf
        return surf
