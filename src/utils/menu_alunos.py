
from datetime import datetime

from controller.controller_aluno import ControllerAluno
from utils.config import confirmar, ler_id, ler_texto

controller = ControllerAluno()


def listar() -> bool:
    """Lista os alunos cadastrados no MongoDB."""
    alunos = controller.listar()

    print("\n---------------- ALUNOS CADASTRADOS ----------------")

    if not alunos:
        print("Nenhum aluno cadastrado.")
        return False

    for aluno in alunos:
        print(f"ID: {aluno[0]:<4} | Nome: {aluno[1]:<22} | E-mail: {aluno[2]}")

    return True


def inserir():
    print("\n================ CADASTRAR ALUNO ================")

    nome = ler_texto("Nome")
    email = ler_texto("E-mail")

    # Verifica se o documento ja existe antes de inserir
    if controller.existe_email(email):
        print(f"\nJá existe um aluno cadastrado com o e-mail {email}.")
        return

    telefone = ler_texto("Telefone")
    data_nascimento = ler_texto("Data de nascimento (AAAA-MM-DD)")
    genero = ler_texto("Gênero")

    novo_id = controller.inserir(
        nome, email, telefone, data_nascimento, genero
    )

    print("\nAluno cadastrado com sucesso!")
    print(controller.obter(novo_id).to_string())


def atualizar():
    print("\n================ ATUALIZAR ALUNO ================")

    if not listar():
        return

    id_aluno = ler_id("\nID do aluno que deseja atualizar: ")

    if id_aluno is None:
        return

    aluno = controller.obter(id_aluno)

    if aluno is None:
        print("\nAluno não encontrado.")
        return

    print("\nDados atuais:")
    print(aluno.to_string())
    print("\nInforme os novos dados (ENTER mantém o valor atual).")

    nascimento_atual = aluno.get_data_nascimento()

    if isinstance(nascimento_atual, datetime):
        nascimento_atual = nascimento_atual.strftime("%Y-%m-%d")

    nome = ler_texto("Nome", aluno.get_nome_aluno())
    email = ler_texto("E-mail", aluno.get_email_aluno())

    if controller.existe_email(email, ignorar_id=id_aluno):
        print(f"\nJá existe outro aluno com o e-mail {email}.")
        return

    telefone = ler_texto("Telefone", aluno.get_telefone_aluno())
    data_nascimento = ler_texto(
        "Data de nascimento (AAAA-MM-DD)", nascimento_atual
    )
    genero = ler_texto("Gênero", aluno.get_genero())

    controller.atualizar(
        id_aluno, nome, email, telefone, data_nascimento, genero
    )

    # Exibe o documento atualizado conforme o edital
    print("\nAluno atualizado com sucesso!")
    print(controller.obter(id_aluno).to_string())


def excluir():
    print("\n================ EXCLUIR ALUNO ================")

    if not listar():
        return

    id_aluno = ler_id("\nID do aluno que deseja excluir: ")

    if id_aluno is None:
        return

    aluno = controller.obter(id_aluno)

    if aluno is None:
        print("\nAluno não encontrado.")
        return

    print("\nAluno selecionado:")
    print(aluno.to_string())

    if not confirmar("\nTem certeza de que deseja excluir este aluno? (s/n): "):
        print("\nExclusão cancelada. Voltando ao menu principal.")
        return False

    # Verifica se existem documentos relacionados em outras colecoes
    treinos, frequencias = controller.contar_dependentes(id_aluno)

    if treinos > 0 or frequencias > 0:
        print(
            f"\nEste aluno possui {treinos} treino(s) e "
            f"{frequencias} documento(s) de frequência associados."
        )

        print("\nO aluno não pode ser excluído enquanto possuir documentos relacionados.")
        return

    if controller.deletar(id_aluno):
        print("\nAluno excluído com sucesso!")
    else:
        print("\nNão foi possível excluir o aluno.")
