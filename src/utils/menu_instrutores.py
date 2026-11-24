
from controller.controller_instrutor import ControllerInstrutor
from utils.config import confirmar, ler_id, ler_texto

controller = ControllerInstrutor()


def listar() -> bool:
    """Lista os instrutores cadastrados no MongoDB."""
    instrutores = controller.listar()

    print("\n-------------- INSTRUTORES CADASTRADOS --------------")

    if not instrutores:
        print("Nenhum instrutor cadastrado.")
        return False

    for instrutor in instrutores:
        print(f"ID: {instrutor[0]:<4} | Nome: {instrutor[1]:<22} | E-mail: {instrutor[2]}")

    return True


def inserir():
    print("\n============== CADASTRAR INSTRUTOR ==============")

    nome = ler_texto("Nome")
    email = ler_texto("E-mail")

    # Verifica se o documento ja existe antes de inserir
    if controller.existe_email(email):
        print(f"\nJá existe um instrutor cadastrado com o e-mail {email}.")
        return

    telefone = ler_texto("Telefone")

    novo_id = controller.inserir(nome, email, telefone)

    print("\nInstrutor cadastrado com sucesso!")
    print(controller.obter(novo_id).to_string())


def atualizar():
    print("\n============== ATUALIZAR INSTRUTOR ==============")

    if not listar():
        return

    id_instrutor = ler_id("\nID do instrutor que deseja atualizar: ")

    if id_instrutor is None:
        return

    instrutor = controller.obter(id_instrutor)

    if instrutor is None:
        print("\nInstrutor não encontrado.")
        return

    print("\nDados atuais:")
    print(instrutor.to_string())
    print("\nInforme os novos dados (ENTER mantém o valor atual).")

    nome = ler_texto("Nome", instrutor.get_nome_instrutor())
    email = ler_texto("E-mail", instrutor.get_email_instrutor())

    if controller.existe_email(email, ignorar_id=id_instrutor):
        print(f"\nJá existe outro instrutor com o e-mail {email}.")
        return

    telefone = ler_texto("Telefone", instrutor.get_telefone_instrutor())

    controller.atualizar(id_instrutor, nome, email, telefone)

    # Exibe o documento atualizado conforme o edital
    print("\nInstrutor atualizado com sucesso!")
    print(controller.obter(id_instrutor).to_string())


def excluir():
    print("\n=============== EXCLUIR INSTRUTOR ===============")

    if not listar():
        return

    id_instrutor = ler_id("\nID do instrutor que deseja excluir: ")

    if id_instrutor is None:
        return

    instrutor = controller.obter(id_instrutor)

    if instrutor is None:
        print("\nInstrutor não encontrado.")
        return

    print("\nInstrutor selecionado:")
    print(instrutor.to_string())

    if not confirmar("\nTem certeza de que deseja excluir este instrutor? (s/n): "):
        print("\nExclusão cancelada. Voltando ao menu principal.")
        return False

    # Verifica se existem treinos associados ao instrutor
    treinos = controller.contar_treinos(id_instrutor)

    if treinos > 0:
        print(f"\nEste instrutor orienta {treinos} treino(s).")
        print("O instrutor não pode ser excluído enquanto possuir treinos relacionados.")
        return

    controller.deletar(id_instrutor)
    print("\nInstrutor excluído com sucesso!")
