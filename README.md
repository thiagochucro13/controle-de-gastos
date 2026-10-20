# Meu Controle de Gastos

Projeto escolar feito em Python para registrar receitas e despesas, calcular o saldo e consultar o histórico de movimentações. A aplicação usa uma interface web local, sem Flask, e salva os dados em SQLite.

## Como executar

1. Instale o Python 3.10 ou superior, se ainda não estiver instalado.
2. Extraia a pasta do projeto.
3. Abra essa pasta no VS Code.
4. Abra o terminal do VS Code.
5. Execute:

   ```bash
   python app.py
   ```

6. Abra no navegador: http://127.0.0.1:8000
7. Crie uma conta de teste e registre algumas receitas e despesas.
8. Para encerrar o servidor, use `Ctrl+C` no terminal.

Não é necessário instalar bibliotecas externas. O projeto usa apenas módulos da biblioteca padrão do Python.

## Bibliotecas utilizadas

| Biblioteca/módulo | Versão | Uso |
|---|---|---|
| Python | 3.10+ | Linguagem principal |
| `http.server` | incluso no Python | Servidor web local |
| `sqlite3` | incluso no Python | Banco de dados SQLite |
| `urllib.parse` | incluso no Python | Leitura dos formulários |
| `http.cookies` | incluso no Python | Cookie de sessão simples |
| `hashlib` | incluso no Python | Hash demonstrativo das senhas |
| `abc` | incluso no Python | Classe abstrata |
| `secrets` | incluso no Python | Token de sessão |
| `html` | incluso no Python | Escapar textos exibidos |

Não há dependências externas nem arquivo `requirements.txt` necessário.

## Estrutura de pastas

```text
controle_de_gastos/
├── app.py                 # Rotas e interface web
├── models.py              # Classes Transacao, Receita e Despesa
├── services.py             # Regras de negócio e cálculo do saldo
├── database.py             # Salvamento e consulta no SQLite
├── static/
│   └── style.css           # Aparência das páginas
├── prints/                 # Adicione aqui capturas reais do programa
└── README.md               # Informações do projeto
```

O arquivo `controle_gastos.db` é criado automaticamente quando a aplicação inicia.

## Princípios de orientação a objetos

- **Encapsulamento:** os dados internos da classe `Transacao` usam atributos protegidos por convenção (`_descricao`, `_valor` e `_categoria`) e propriedades para leitura.
- **Herança:** `Receita` e `Despesa` herdam da classe `Transacao`.
- **Polimorfismo:** cada classe filha implementa `tipo()` e retorna seu tipo de movimentação.
- **Abstração:** `Transacao` é uma classe abstrata e exige que as classes filhas implementem `tipo()`.

## Separação de responsabilidades

- `app.py`: recebe requisições e mostra as páginas.
- `services.py`: aplica as regras do sistema.
- `database.py`: trabalha com o banco de dados.
- `models.py`: define as entidades e seus comportamentos.

## Testes manuais

- Criar uma conta com um e-mail novo.
- Tentar cadastrar novamente o mesmo e-mail.
- Entrar com a conta criada.
- Adicionar uma receita e uma despesa.
- Conferir se o saldo é calculado corretamente.
- Excluir uma movimentação.
- Fechar e abrir o site novamente e verificar se os dados continuam salvos.

## Capturas de tela

Depois de executar o projeto, tire capturas reais do navegador mostrando:
1. Tela de login e cadastro.
2. Painel com receitas, despesas e saldo.
3. Histórico com algumas movimentações.

Salve as imagens na pasta `prints/` e insira-as aqui, por exemplo:

```markdown
![Painel do sistema](prints/painel.png)
```

Não inclua imagens de exemplo como se fossem capturas reais do programa.

## Limitações e observações

Este projeto é uma demonstração escolar para rodar localmente. Antes de publicar para uso real, é necessário reforçar a segurança, especialmente o armazenamento de senhas, o gerenciamento de sessões, a proteção contra requisições indevidas e a configuração do servidor. Use apenas dados e senhas de teste.

## Autor

Projeto escolar — responsável: Thiago Ramoni Correa.
