
from datetime import datetime

from conexion.mongo_queries import MongoQueries
from controller.controller_aluno import ControllerAluno
from model.treino import Treino


class ControllerTreino:
    """Controlador CRUD da coleção TREINO no MongoDB."""

    @staticmethod
    def _validar(nome_treino, objetivo):
        if not nome_treino or not nome_treino.strip():
            raise ValueError("O nome do treino é obrigatório.")

        if not objetivo or not objetivo.strip():
            raise ValueError("O objetivo do treino é obrigatório.")

    @staticmethod
    def _documento_para_tupla(documento):
        if documento is None:
            return None

        return (
            documento.get("ID_TREINO"),
            documento.get("ID_ALUNO"),
            documento.get("ID_INSTRUTOR"),
            documento.get("NOME_TREINO"),
            documento.get("OBJETIVO"),
            documento.get("DATA_CRIACAO")
        )

    @staticmethod
    def _validar_relacionamentos(banco, id_aluno, id_instrutor):
        """Verifica se o aluno e o instrutor existem."""
        if banco["ALUNO"].find_one({"ID_ALUNO": id_aluno}) is None:
            raise ValueError("Aluno não encontrado.")

        if banco["INSTRUTOR"].find_one(
            {"ID_INSTRUTOR": id_instrutor}
        ) is None:
            raise ValueError("Instrutor não encontrado.")

    def inserir(self, id_aluno, id_instrutor, nome_treino, objetivo=""):
        """Cadastra um treino relacionado a um aluno e instrutor."""
        self._validar(nome_treino, objetivo)

        id_aluno = int(id_aluno)
        id_instrutor = int(id_instrutor)

        mongo = MongoQueries()

        try:
            banco = mongo.conectar()
            colecao = banco["TREINO"]

            self._validar_relacionamentos(
                banco, id_aluno, id_instrutor
            )

            ultimo = colecao.find_one(
                sort=[("ID_TREINO", -1)]
            )

            novo_id = (
                int(ultimo["ID_TREINO"]) + 1
                if ultimo else 1
            )

            documento = {
                "ID_TREINO": novo_id,
                "ID_ALUNO": id_aluno,
                "ID_INSTRUTOR": id_instrutor,
                "NOME_TREINO": nome_treino.strip(),
                "OBJETIVO": objetivo.strip(),
                "DATA_CRIACAO": datetime.now()
            }

            colecao.insert_one(documento)
            return novo_id

        finally:
            mongo.fechar()

    def atualizar(
        self, id_treino, id_aluno, id_instrutor,
        nome_treino, objetivo=""
    ):
        """Atualiza os dados de um treino existente."""
        self._validar(nome_treino, objetivo)

        id_treino = int(id_treino)
        id_aluno = int(id_aluno)
        id_instrutor = int(id_instrutor)

        mongo = MongoQueries()

        try:
            banco = mongo.conectar()

            self._validar_relacionamentos(
                banco, id_aluno, id_instrutor
            )

            resultado = banco["TREINO"].update_one(
                {"ID_TREINO": id_treino},
                {
                    "$set": {
                        "ID_ALUNO": id_aluno,
                        "ID_INSTRUTOR": id_instrutor,
                        "NOME_TREINO": nome_treino.strip(),
                        "OBJETIVO": objetivo.strip()
                    }
                }
            )

            return resultado.matched_count > 0

        finally:
            mongo.fechar()

    def deletar(self, id_treino):
        """Exclui um treino pelo ID."""
        mongo = MongoQueries()

        try:
            banco = mongo.conectar()

            resultado = banco["TREINO"].delete_one(
                {"ID_TREINO": int(id_treino)}
            )

            return resultado.deleted_count > 0

        finally:
            mongo.fechar()

    def buscar_por_id(self, id_treino):
        """Busca um treino pelo ID."""
        mongo = MongoQueries()

        try:
            banco = mongo.conectar()

            documento = banco["TREINO"].find_one(
                {"ID_TREINO": int(id_treino)}
            )

            return self._documento_para_tupla(documento)

        finally:
            mongo.fechar()

    def listar(self):
        """Lista treinos com nomes de alunos e instrutores."""
        mongo = MongoQueries()

        try:
            banco = mongo.conectar()

            pipeline = [
                {
                    "$lookup": {
                        "from": "ALUNO",
                        "localField": "ID_ALUNO",
                        "foreignField": "ID_ALUNO",
                        "as": "aluno"
                    }
                },
                {"$unwind": "$aluno"},
                {
                    "$lookup": {
                        "from": "INSTRUTOR",
                        "localField": "ID_INSTRUTOR",
                        "foreignField": "ID_INSTRUTOR",
                        "as": "instrutor"
                    }
                },
                {"$unwind": "$instrutor"},
                {"$sort": {"DATA_CRIACAO": -1}}
            ]

            documentos = banco["TREINO"].aggregate(pipeline)

            return [
                (
                    doc.get("ID_TREINO"),
                    doc["aluno"].get("NOME_ALUNO"),
                    doc["instrutor"].get("NOME_INSTRUTOR"),
                    doc.get("NOME_TREINO"),
                    doc.get("OBJETIVO"),
                    doc.get("DATA_CRIACAO")
                )
                for doc in documentos
            ]

        finally:
            mongo.fechar()

    def obter(self, id_treino):
        """Retorna um objeto Treino com Aluno e Instrutor."""
        linha = self.buscar_por_id(id_treino)

        if not linha:
            return None

        aluno = ControllerAluno().obter(linha[1])

        mongo = MongoQueries()
        try:
            banco = mongo.conectar()

            documento_instrutor = banco["INSTRUTOR"].find_one(
                {"ID_INSTRUTOR": int(linha[2])}
            )
        finally:
            mongo.fechar()

        if aluno is None or documento_instrutor is None:
            return None

        # O modelo Instrutor será integrado com a parte
        # desenvolvida pela colega responsável.
        from model.instrutor import Instrutor

        instrutor = Instrutor(
            documento_instrutor["ID_INSTRUTOR"],
            documento_instrutor["NOME_INSTRUTOR"],
            documento_instrutor["EMAIL_INSTRUTOR"],
            documento_instrutor["TELEFONE_INSTRUTOR"]
        )

        return Treino(
            linha[0],
            aluno,
            instrutor,
            linha[3],
            linha[4],
            linha[5]
        )

    def listar_por_aluno(self, id_aluno):
        """Lista os treinos associados a um aluno."""
        mongo = MongoQueries()

        try:
            banco = mongo.conectar()

            pipeline = [
                {"$match": {"ID_ALUNO": int(id_aluno)}},
                {
                    "$lookup": {
                        "from": "INSTRUTOR",
                        "localField": "ID_INSTRUTOR",
                        "foreignField": "ID_INSTRUTOR",
                        "as": "instrutor"
                    }
                },
                {"$unwind": "$instrutor"},
                {"$sort": {"DATA_CRIACAO": -1}}
            ]

            documentos = banco["TREINO"].aggregate(pipeline)

            return [
                (
                    doc.get("ID_TREINO"),
                    doc["instrutor"].get("NOME_INSTRUTOR"),
                    doc.get("NOME_TREINO"),
                    doc.get("OBJETIVO"),
                    doc.get("DATA_CRIACAO")
                )
                for doc in documentos
            ]

        finally:
            mongo.fechar()
