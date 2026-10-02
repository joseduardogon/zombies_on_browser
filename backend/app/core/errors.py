"""Erros de dominio do jogo."""


class GameError(Exception):
    """Violacao de uma regra do jogo.

    Attributes:
        message: Descricao legivel do problema.
        status_code: Status HTTP que a API deve responder.
    """

    def __init__(self, message: str, status_code: int = 400) -> None:
        """Cria o erro.

        Args:
            message: Descricao legivel do problema.
            status_code: Status HTTP correspondente.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
