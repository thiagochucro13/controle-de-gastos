from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from http.cookies import SimpleCookie
from database import BancoDeDados
from services import ServicoFinanceiro
from models import Receita, Despesa
import hashlib
import secrets
import html

HOST = "127.0.0.1"
PORT = 8000
db = BancoDeDados()
service = ServicoFinanceiro(db)
sessoes = {}

def hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def pagina(titulo, conteudo):
    return f"""<!doctype html>
<html lang="pt-br"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title><link rel="stylesheet" href="/static/style.css"></head>
<body><main class="container"><header><h1>Meu Controle de Gastos</h1>
<p>Organize suas receitas e despesas de um jeito simples.</p></header>{conteudo}
<footer>Projeto escolar • Python + SQLite</footer></main></body></html>"""

def campo(nome, tipo="text", placeholder=""):
    return f'<label>{nome}<input name="{nome.lower()}" type="{tipo}" placeholder="{placeholder}" required></label>'

class AplicacaoHandler(BaseHTTPRequestHandler):
    def responder(self, status, corpo, cookie=None):
        corpo_bytes = corpo.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo_bytes)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(corpo_bytes)

    def dados_formulario(self):
        tamanho = int(self.headers.get("Content-Length", 0))
        dados = self.rfile.read(tamanho).decode("utf-8")
        return {k: v[0] for k, v in parse_qs(dados).items()}

    def usuario_atual(self):
        cookie = SimpleCookie(self.headers.get("Cookie"))
        token = cookie["sessao"].value if "sessao" in cookie else None
        return sessoes.get(token)

    def do_GET(self):
        if self.path.startswith("/static/"):
            caminho = os.path.join(os.path.dirname(__file__), self.path.lstrip("/"))
            try:
                with open(caminho, "rb") as arquivo:
                    conteudo = arquivo.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/css; charset=utf-8")
                self.end_headers()
                self.wfile.write(conteudo)
            except FileNotFoundError:
                self.responder(404, pagina("Erro", "<p>Arquivo não encontrado.</p>"))
            return

        usuario = self.usuario_atual()
        if self.path == "/sair":
            cookie = "sessao=; Max-Age=0; Path=/; HttpOnly"
            self.responder(200, pagina("Saiu", '<p>Você saiu da conta.</p><a class="botao" href="/">Voltar ao início</a>'), cookie)
            return
        if usuario:
            self.responder(200, self.painel(usuario))
        else:
            conteudo = """
            <section class="card"><h2>Entrar</h2>
            <form method="post" action="/login">
            <label>E-mail<input name="email" type="email" required></label>
            <label>Senha<input name="senha" type="password" required></label>
            <button>Entrar</button></form></section>
            <section class="card"><h2>Criar conta</h2>
            <form method="post" action="/cadastro">
            <label>Nome<input name="nome" required></label>
            <label>E-mail<input name="email" type="email" required></label>
            <label>Senha<input name="senha" type="password" minlength="4" required></label>
            <button>Cadastrar</button></form></section>
            <p class="aviso">Projeto demonstrativo para uso local. Não use uma senha real.</p>"""
            self.responder(200, pagina("Login", conteudo))

    def do_POST(self):
        dados = self.dados_formulario()
        if self.path == "/cadastro":
            try:
                self.db_usuario_criar(dados)
                self.responder(200, pagina("Conta criada", '<p>Conta criada! Agora faça login.</p><a class="botao" href="/">Ir para login</a>'))
            except ValueError as erro:
                self.responder(400, pagina("Aviso", f"<p>{html.escape(str(erro))}</p><a href='/'>Voltar</a>"))
            return
        if self.path == "/login":
            usuario = service.autenticar(dados.get("email", "").strip().lower(), hash_senha(dados.get("senha", "")))
            if not usuario:
                self.responder(401, pagina("Erro", '<p>E-mail ou senha incorretos.</p><a href="/">Tentar novamente</a>'))
                return
            token = secrets.token_urlsafe(24)
            sessoes[token] = usuario
            self.responder(200, self.painel(usuario), f"sessao={token}; Path=/; HttpOnly; SameSite=Lax")
            return

        usuario = self.usuario_atual()
        if not usuario:
            self.responder(401, pagina("Login necessário", '<p>Entre na sua conta primeiro.</p><a href="/">Voltar</a>'))
            return
        try:
            if self.path == "/transacao":
                tipo = dados.get("tipo")
                descricao = dados.get("descricao", "").strip()
                categoria = dados.get("categoria", "").strip()
                valor = float(dados.get("valor", "0").replace(",", "."))
                if tipo == "receita":
                    transacao = Receita(descricao, valor, categoria)
                else:
                    transacao = Despesa(descricao, valor, categoria)
                service.adicionar_transacao(usuario["id"], transacao)
            elif self.path.startswith("/excluir/"):
                service.excluir_transacao(usuario["id"], int(self.path.split("/")[-1]))
            self.responder(200, self.painel(usuario))
        except (ValueError, KeyError) as erro:
            self.responder(400, pagina("Aviso", f"<p>Não foi possível concluir: {html.escape(str(erro))}</p><a href='/'>Voltar</a>"))

    def db_usuario_criar(self, dados):
        nome = dados.get("nome", "").strip()
        email = dados.get("email", "").strip().lower()
        senha = dados.get("senha", "")
        if not nome or not email or len(senha) < 4:
            raise ValueError("Preencha os campos e use uma senha com pelo menos 4 caracteres.")
        self.server.db.criar_usuario(nome, email, hash_senha(senha))

    def painel(self, usuario):
        resumo = service.resumo(usuario["id"])
        transacoes = service.listar_transacoes(usuario["id"])
        linhas = "".join(
            f"<tr><td>{html.escape(t['descricao'])}</td><td>{html.escape(t['tipo'].capitalize())}</td>"
            f"<td>{html.escape(t['categoria'])}</td><td>R$ {t['valor']:.2f}</td>"
            f"<td><form method='post' action='/excluir/{t['id']}'><button class='excluir'>Excluir</button></form></td></tr>"
            for t in transacoes
        ) or "<tr><td colspan='5'>Nenhuma movimentação cadastrada ainda.</td></tr>"
        conteudo = f"""
        <section class="welcome"><div><h2>Olá, {html.escape(usuario['nome'])}!</h2>
        <p>Confira como estão suas finanças.</p></div><a href="/sair">Sair</a></section>
        <section class="resumo">
        <div class="card"><span>Receitas</span><strong>R$ {resumo['receitas']:.2f}</strong></div>
        <div class="card"><span>Despesas</span><strong>R$ {resumo['despesas']:.2f}</strong></div>
        <div class="card"><span>Saldo</span><strong>R$ {resumo['saldo']:.2f}</strong></div></section>
        <section class="card"><h2>Adicionar movimentação</h2>
        <form method="post" action="/transacao">
        <label>Descrição<input name="descricao" required></label>
        <label>Valor (R$)<input name="valor" type="number" min="0.01" step="0.01" required></label>
        <label>Tipo<select name="tipo"><option value="despesa">Despesa</option><option value="receita">Receita</option></select></label>
        <label>Categoria<input name="categoria" placeholder="Ex.: alimentação" required></label>
        <button>Salvar movimentação</button></form></section>
        <section class="card"><h2>Histórico</h2><div class="table-wrap"><table>
        <thead><tr><th>Descrição</th><th>Tipo</th><th>Categoria</th><th>Valor</th><th>Ação</th></tr></thead>
        <tbody>{linhas}</tbody></table></div></section>"""
        return pagina("Painel", conteudo)

    def log_message(self, format, *args):
        pass

class Servidor(HTTPServer):
    def __init__(self, endereco, handler):
        super().__init__(endereco, handler)
        self.db = db

if __name__ == "__main__":
    print(f"Abra http://{HOST}:{PORT} no navegador.")
    print("Para encerrar, volte ao terminal e aperte Ctrl+C.")
    Servidor((HOST, PORT), AplicacaoHandler).serve_forever()
