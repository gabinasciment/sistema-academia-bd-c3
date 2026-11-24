
###########################################################################
# Menus do sistema e funções de apoio da interface (console)
# Sistema de Academia - C3 - MongoDB
###########################################################################

from pymongo.errors import DuplicateKeyError, ConnectionFailure

LINHA = "=" * 50

MENU_PRINCIPAL = f"""
{LINHA}
                 MENU PRINCIPAL
{LINHA}
1 - Relatórios
2 - Inserir documentos
3 - Remover documentos
4 - Atualizar documentos
5 - Sair
{LINHA}"""

MENU_RELATORIOS = f"""
{LINHA}
                   RELATÓRIOS
{LINHA}
1 - Quantidade de treinos por aluno (agrupamento)
2 - Treinos com alunos e instrutores (junção)
3 - Treinos de um aluno
4 - Frequências de um aluno
0 - Voltar ao menu principal
{LINHA}"""

MENU_ENTIDADES = f"""
{LINHA}
{{titulo}}
{LINHA}
1 - Alunos
2 - Instrutores
3 - Treinos
4 - Frequências
0 - Voltar ao menu principal
{LINHA}"""


# Tratamento de erros do MongoDB
def mensagem_erro(erro: Exception) -> str:
    if isinstance(erro, DuplicateKeyError):
        return "Já existe um documento com esse valor."

    if isinstance(erro, ConnectionFailure):
        return "Não foi possível conectar ao MongoDB."

    return f"Não foi possível realizar a operação: {erro}"


# Confirmação de operações
def confirmar(pergunta: str) -> bool:
    while True:
        resposta = input(pergunta).strip().lower()

        if resposta in ("s", "sim"):
            return True

        if resposta in ("n", "nao", "não"):
            return False

        print("Responda com S (sim) ou N (não).")


# Leitura e validação de IDs
def ler_id(mensagem: str):
    valor = input(mensagem).strip()

    if not valor.isdecimal() or int(valor) <= 0:
        print("\nInforme um ID numérico válido.")
        return None

    return int(valor)


# Leitura de textos
def ler_texto(rotulo: str, atual=None) -> str:
    if atual is None:
        return input(f"{rotulo}: ").strip()

    valor = input(f"{rotulo} [{atual}]: ").strip()

    return valor if valor else str(atual)


# Controle da repetição das operações
def executar_operacao(operacao, pergunta_repetir: str):
    while True:
        try:
            if operacao() is False:
                return

        except ValueError as erro:
            print(f"\nDados inválidos: {erro}")

        except Exception as erro:
            print("\n" + mensagem_erro(erro))

        if not confirmar(f"\n{pergunta_repetir} (s/n): "):
            return
