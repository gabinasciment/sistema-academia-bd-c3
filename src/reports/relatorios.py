
import os
import json

from conexion.mongo_queries import MongoQueries


# Pasta src/sql encontrada a partir deste arquivo
PASTA_SQL = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "sql"
)


def ler_mongo(nome_arquivo: str) -> list:
    with open(
        os.path.join(PASTA_SQL, nome_arquivo),
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


class Relatorio:

    def __init__(self):
        self.query_relatorio_treinos_por_aluno = ler_mongo(
            "relatorio_treinos_por_aluno.json"
        )

        self.query_relatorio_treinos_com_instrutores = ler_mongo(
            "relatorio_treinos_com_instrutores.json"
        )

    def exibir(self, titulo: str, colecao: str, query: list):

        mongo = MongoQueries()

        try:
            mongo.connect()

            resultado = list(
                mongo.db[colecao].aggregate(query)
            )

        finally:
            mongo.close()

        print("\n" + "=" * 70)
        print(titulo.center(70))
        print("=" * 70)

        if not resultado:
            print("Nenhum registro encontrado.")
        else:
            for registro in resultado:
                for campo, valor in registro.items():
                    print(f"{campo}: {valor}")
                print("-" * 50)

        input("\nPressione ENTER para voltar ao menu de relatórios...")

    def get_relatorio_treinos_por_aluno(self):
        self.exibir(
            "QUANTIDADE DE TREINOS POR ALUNO",
            "ALUNO",
            self.query_relatorio_treinos_por_aluno
        )

    def get_relatorio_treinos_com_instrutores(self):
        self.exibir(
            "TREINOS COM ALUNOS E INSTRUTORES",
            "TREINO",
            self.query_relatorio_treinos_com_instrutores
        )
