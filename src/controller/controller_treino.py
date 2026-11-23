
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
            documento.get("id_treino"),
            documento.get("id_aluno"),
            documento.get("id_instrutor"),
            documento.get("nome_treino"),
            documento.get("objetivo"),
            documento.get("data_criacao")
        )

    @staticmethod
    def _validar_relacionamentos(banco, id_aluno, id_instrutor):
        """Verifica se o aluno e o instrutor existem."""
        if banco["aluno"].find_one({"id_aluno": id_aluno}) is None:
            raise ValueError("Aluno não encontrado.")

        if banco["instrutor"].find_one(
            {"id_instrutor": id_instrutor}
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
            colecao = banco["treino"]

            self._validar_relacionamentos(
                banco, id_aluno, id_instrutor
            )

            ultimo = colecao.find_one(
                sort=[("id_treino", -1)]
            )

            novo_id = (
                int(ultimo["id_treino"]) + 1
                if ultimo else 1
            )

            documento = {
                "id_treino": novo_id,
                "id_aluno": id_aluno,
                "id_instrutor": id_instrutor,
                "nome_treino": nome_treino.strip(),
                "objetivo": objetivo.strip(),
                "data_criacao": datetime.now()
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

            resultado = banco["treino"].update_one(
                {"id_treino": id_treino},
                {
                    "$set": {
                        "id_aluno": id_aluno,
                        "id_instrutor": id_instrutor,
                        "nome_treino": nome_treino.strip(),
                        "objetivo": objetivo.strip()
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

            resultado = banco["treino"].delete_one(
                {"id_treino": int(id_treino)}
            )

            return resultado.deleted_count > 0

        finally:
            mongo.fechar()

    def buscar_por_id(self, id_treino):
        """Busca um treino pelo ID."""
        mongo = MongoQueries()

        try:
            banco = mongo.conectar()

            documento = banco["treino"].find_one(
                {"id_treino": int(id_treino)}
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
                        "from": "aluno",
                        "localField": "id_aluno",
                        "foreignField": "id_aluno",
                        "as": "aluno"
                    }
                },
                {"$unwind": "$aluno"},
                {
                    "$lookup": {
                        "from": "instrutor",
                        "localField": "id_instrutor",
                        "foreignField": "id_instrutor",
                        "as": "instrutor"
                    }
                },
                {"$unwind": "$instrutor"},
                {"$sort": {"data_criacao": -1}}
            ]

            documentos = banco["treino"].aggregate(pipeline)

            return [
                (
                    doc.get("id_treino"),
                    doc["aluno"].get("nome_aluno"),
                    doc["instrutor"].get("nome_instrutor"),
                    doc.get("nome_treino"),
                    doc.get("objetivo"),
                    doc.get("data_criacao")
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

            documento_instrutor = banco["instrutor"].find_one(
                {"id_instrutor": int(linha[2])}
            )
        finally:
            mongo.fechar()

        if aluno is None or documento_instrutor is None:
            return None

        # O modelo Instrutor será integrado com a parte
        # desenvolvida pela colega responsável.
        from model.instrutor import Instrutor

        instrutor = Instrutor(
            documento_instrutor["id_instrutor"],
            documento_instrutor["nome_instrutor"],
            documento_instrutor["email_instrutor"],
            documento_instrutor["telefone_instrutor"]
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
                {"$match": {"id_aluno": int(id_aluno)}},
                {
                    "$lookup": {
                        "from": "instrutor",
                        "localField": "id_instrutor",
                        "foreignField": "id_instrutor",
                        "as": "instrutor"
                    }
                },
                {"$unwind": "$instrutor"},
                {"$sort": {"data_criacao": -1}}
            ]

            documentos = banco["treino"].aggregate(pipeline)

            return [
                (
                    doc.get("id_treino"),
                    doc["instrutor"].get("nome_instrutor"),
                    doc.get("nome_treino"),
                    doc.get("objetivo"),
                    doc.get("data_criacao")
                )
                for doc in documentos
            ]

        finally:
            mongo.fechar()
