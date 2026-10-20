from abc import ABC, abstractmethod

class Transacao(ABC):
    """Classe abstrata que define o comportamento comum das movimentações."""

    def __init__(self, descricao, valor, categoria):
        descricao = descricao.strip()
        categoria = categoria.strip()
        valor = float(valor)
        if not descricao or not categoria:
            raise ValueError("Descrição e categoria são obrigatórias.")
        if valor <= 0:
            raise ValueError("O valor precisa ser maior que zero.")
        self._descricao = descricao
        self._valor = valor
        self._categoria = categoria

    @property
    def descricao(self):
        return self._descricao

    @property
    def valor(self):
        return self._valor

    @property
    def categoria(self):
        return self._categoria

    @abstractmethod
    def tipo(self):
        """Cada classe filha informa seu próprio tipo."""
        raise NotImplementedError

class Receita(Transacao):
    def tipo(self):
        return "receita"

class Despesa(Transacao):
    def tipo(self):
        return "despesa"
