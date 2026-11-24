
###########################################################################
# Programa principal do Sistema de Academia
# Disciplina: Banco de Dados
# C3 - MongoDB
###########################################################################

from importlib import import_module

from utils.splash_screen import exibir_splash
from utils.config import (
    MENU_PRINCIPAL,
    MENU_ENTIDADES,
    MENU_RELATORIOS,
    executar_operacao,
    mensagem_erro
)


# Modulos responsaveis pelas entidades do sistema
ENTIDADES = {
    "1": "utils.menu_alunos",
    "2": "utils.menu_instrutores",
    "3": "utils.menu_treinos",
    "4": "utils.menu_frequencias"
}


# Menu de insercao, remocao e atualizacao de documentos
def menu_operacoes(titulo, operacao, pergunta_repetir):

    while True:
        print(MENU_ENTIDADES.format(titulo=titulo))

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "0":
            return

        if opcao not in ENTIDADES:
            print("\nOpção inválida. Tente novamente.")
            continue

        try:
            modulo = import_module(ENTIDADES[opcao])

            funcao = getattr(modulo, operacao)

            executar_operacao(funcao, pergunta_repetir)

            return

        except ModuleNotFoundError:
            print("\nEsta funcionalidade ainda não está disponível.")
            print("Verifique se o controller correspondente foi implementado.")

        except Exception as erro:
            print("\n" + mensagem_erro(erro))


# Menu de insercao
def inserir():
    menu_operacoes(
        "INSERIR DOCUMENTOS",
        "inserir",
        "Deseja inserir outro documento?"
    )


# Menu de remocao
def excluir():
    menu_operacoes(
        "REMOVER DOCUMENTOS",
        "excluir",
        "Deseja remover outro documento?"
    )


# Menu de atualizacao
def atualizar():
    menu_operacoes(
        "ATUALIZAR DOCUMENTOS",
        "atualizar",
        "Deseja atualizar outro documento?"
    )


# Menu de relatorios
def relatorios():

    while True:
        print(MENU_RELATORIOS)

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "0":
            return

        try:
            if opcao in ("1", "2"):
                # Integracao pendente com o modulo de relatorios
                print("\nRelatório aguardando integração.")

            elif opcao == "3":
                from utils import menu_treinos
                menu_treinos.listar_por_aluno()

            elif opcao == "4":
                from utils import menu_frequencias
                menu_frequencias.listar_por_aluno()

            else:
                print("\nOpção inválida. Tente novamente.")

        except ModuleNotFoundError:
            print("\nEsta funcionalidade ainda não está disponível.")

        except Exception as erro:
            print("\n" + mensagem_erro(erro))


# Funcao principal do sistema
def main():

    # Exibe a tela de apresentacao
    exibir_splash()

    while True:

        print(MENU_PRINCIPAL)

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            relatorios()

        elif opcao == "2":
            inserir()

        elif opcao == "3":
            excluir()

        elif opcao == "4":
            atualizar()

        elif opcao == "5":
            print("\nSistema encerrado com sucesso!")
            print("Obrigado por utilizar o Sistema de Academia.")
            break

        else:
            print("\nOpção inválida. Tente novamente.")


# Ponto de entrada da aplicacao
if __name__ == "__main__":
    try:
        main()

    except (KeyboardInterrupt, EOFError):
        print("\n\nSistema encerrado pelo usuário.")
