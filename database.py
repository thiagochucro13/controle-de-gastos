import sqlite3

class BancoDeDados:
    """Responsável apenas pela persistência das informações."""

    def __init__(self, caminho="controle_gastos.db"):
        self._caminho = caminho
        self._criar_tabelas()

    def conectar(self):
        conexao = sqlite3.connect(self._caminho)
        conexao.row_factory = sqlite3.Row
        return conexao

    def _criar_tabelas(self):
        with self.conectar() as conexao:
            conexao.execute("""CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL
            )""")
            conexao.execute("""CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                tipo TEXT NOT NULL,
                categoria TEXT NOT NULL,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
            )""")

    def criar_usuario(self, nome, email, senha_hash):
        try:
            with self.conectar() as conexao:
                conexao.execute(
                    "INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)",
                    (nome, email, senha_hash)
                )
        except sqlite3.IntegrityError:
            raise ValueError("Esse e-mail já está cadastrado.")

    def buscar_usuario(self, email):
        with self.conectar() as conexao:
            linha = conexao.execute(
                "SELECT id, nome, email, senha_hash FROM usuarios WHERE email = ?",
                (email,)
            ).fetchone()
            return dict(linha) if linha else None

    def adicionar_transacao(self, usuario_id, transacao):
        with self.conectar() as conexao:
            conexao.execute(
                """INSERT INTO transacoes
                (usuario_id, descricao, valor, tipo, categoria)
                VALUES (?, ?, ?, ?, ?)""",
                (usuario_id, transacao.descricao, transacao.valor, transacao.tipo(), transacao.categoria)
            )

    def listar_transacoes(self, usuario_id):
        with self.conectar() as conexao:
            linhas = conexao.execute(
                """SELECT id, descricao, valor, tipo, categoria FROM transacoes
                WHERE usuario_id = ? ORDER BY id DESC""", (usuario_id,)
            ).fetchall()
            return [dict(linha) for linha in linhas]

    def excluir_transacao(self, usuario_id, transacao_id):
        with self.conectar() as conexao:
            cursor = conexao.execute(
                "DELETE FROM transacoes WHERE id = ? AND usuario_id = ?",
                (transacao_id, usuario_id)
            )
            if cursor.rowcount == 0:
                raise ValueError("Movimentação não encontrada.")
