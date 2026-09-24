class BatalhaNavalErro(Exception):

    def __init__(self, mensagem: str):
        super().__init__(mensagem)
        self.mensagem = mensagem

class PosicaoInvalidaErro(BatalhaNavalErro):
    pass

class JogadaRepetidaErro(BatalhaNavalErro):
    pass

class NavioSobrepostoErro(BatalhaNavalErro):
    pass

class NavioForaDoTabuleiroErro(BatalhaNavalErro):
    pass

class FrotaIncompletaErro(BatalhaNavalErro):
    pass

class PartidaFinalizadaErro(BatalhaNavalErro):
    pass

class ConexaoRedeErro(BatalhaNavalErro):
    pass
