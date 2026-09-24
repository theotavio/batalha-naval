from __future__ import annotations
import pygame
from frontend.core.gerenciador_assets import GerenciadorAssets

class GerenciadorSom:
    _instancia: GerenciadorSom | None = None

    def __init__(self) -> None:
        self.assets = GerenciadorAssets.obter_instancia()
        self.volume_geral: float = 0.5
        self.volume_musica: float = 0.2
        self.volume_efeitos: float = 0.35
        self.volume_interface: float = 0.2
        self.mudo: bool = False
        self.musica_atual: str | None = None

    @classmethod
    def obter_instancia(cls) -> GerenciadorSom:
        if cls._instancia is None:
            cls._instancia = cls()
        return cls._instancia

    def _e_som_interface(self, nome: str) -> bool:
        return nome.startswith('Sound')

    def tocar_som(self, nome: str) -> None:
        if self.mudo or not pygame.mixer.get_init() or self.volume_geral <= 0.0:
            return
        som = self.assets.obter_som(nome)
        if som:
            if self._e_som_interface(nome):
                vol = self.volume_geral * self.volume_interface
            else:
                vol = self.volume_geral * self.volume_efeitos
            som.set_volume(max(0.0, min(1.0, vol)))
            som.play()

    def tocar_musica(self, nome_faixa: str, loop: bool=True) -> None:
        if not pygame.mixer.get_init():
            return
        chave = nome_faixa.lower()
        if chave in self.assets.musicas:
            caminho = self.assets.musicas[chave]
            try:
                if self.musica_atual != chave:
                    pygame.mixer.music.load(caminho)
                    vol = 0.0 if self.mudo else self.volume_geral * self.volume_musica
                    pygame.mixer.music.set_volume(max(0.0, min(1.0, vol)))
                    pygame.mixer.music.play(-1 if loop else 1)
                    self.musica_atual = chave
            except Exception as e:
                print(f'[Aviso] Falha ao tocar música {nome_faixa}: {e}')

    def parar_musica(self) -> None:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            self.musica_atual = None

    def alternar_mudo(self) -> bool:
        self.mudo = not self.mudo
        self._atualizar_volume_musica()
        return self.mudo

    def definir_volume_geral(self, volume: float) -> None:
        self.volume_geral = max(0.0, min(1.0, volume))
        self._atualizar_volume_musica()

    def definir_volume_musica(self, volume: float) -> None:
        self.volume_musica = max(0.0, min(1.0, volume))
        self._atualizar_volume_musica()

    def definir_volume_efeitos(self, volume: float) -> None:
        self.volume_efeitos = max(0.0, min(1.0, volume))

    def definir_volume_interface(self, volume: float) -> None:
        self.volume_interface = max(0.0, min(1.0, volume))

    def _atualizar_volume_musica(self) -> None:
        if pygame.mixer.get_init():
            if self.mudo:
                pygame.mixer.music.set_volume(0.0)
            else:
                vol = self.volume_geral * self.volume_musica
                pygame.mixer.music.set_volume(max(0.0, min(1.0, vol)))
