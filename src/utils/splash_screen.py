
###########################################################################
# Tela de apresentação do Sistema de Academia
# Sistema de Academia - C3 - MongoDB
###########################################################################

import time
from conexion.mongo_queries import MongoQueries
from utils.config import mensagem_erro


def exibir_splash():
    print("=" * 60)
    print("                 SISTEMA DE ACADEMIA")
    print("=" * 60)
    print("Disciplina: Banco de Dados")
    print("Professor: Howard Roatti")
    print("Semestre: 2026/2")
    print("Banco de Dados: MongoDB")
    print()
    print("Componentes do grupo:")
    print("  Esther Bagatelli")
    print("  Érika Pimenta")
    print("  Gabriela Nascimento")
    print("  Laysa Costa")
    print("  Lara Marchesi")
    print("  Caio Ferrari")
    print()
    print("-" * 60)
    print("QUANTIDADE DE DOCUMENTOS POR COLEÇÃO")
    print("-" * 60)

    mongo = None

    try:
        mongo = MongoQueries()
        banco = mongo.conectar()

        colecoes = ["aluno", "instrutor", "treino", "frequencia"]

        for colecao in colecoes:
            total = banco[colecao].count_documents({})

            print(f"{colecao.capitalize():<15}: {total}")

    except Exception as erro:
        print("\nNão foi possível consultar os documentos no MongoDB.")
        print(mensagem_erro(erro))

    finally:
        if mongo is not None:
            mongo.close()

    print("=" * 60)
    print()
    time.sleep(2)
