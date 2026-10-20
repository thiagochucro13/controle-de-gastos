from models import Receita, Despesa

class ServicoFinanceiro:
    """Contém as regras de negócio, sem cuidar das páginas web."""

    def __init__(self, banco):
        self._banco = banco

    def autenticar(self, email, senha_hash):
        usuario = self._banco.buscar_usuario(email)
        if usuario and usuario["senha_hash"] == senha_hash:
            usuario.pop("senha_hash", None)
            return usuario
        return None

    def adicionar_transacao(self, usuario_id, transacao):
        if not isinstance(transacao, (Receita, Despesa)):
            raise ValueError("Tipo de movimentação inválido.")
        self._banco.adicionar_transacao(usuario_id, transacao)

    def listar_transacoes(self, usuario_id):
        return self._banco.listar_transacoes(usuario_id)

    def excluir_transacao(self, usuario_id, transacao_id):
        self._banco.excluir_transacao(usuario_id, transacao_id)

    def resumo(self, usuario_id):
        transacoes = self.listar_transacoes(usuario_id)
        receitas = sum(t["valor"] for t in transacoes if t["tipo"] == "receita")
        despesas = sum(t["valor"] for t in transacoes if t["tipo"] == "despesa")
        return {"receitas": receitas, "despesas": despesas, "saldo": receitas - despesas}
