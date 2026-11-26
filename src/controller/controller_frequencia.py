
from datetime import datetime

from conexion.mongo_queries import MongoQueries
from controller.controller_aluno import ControllerAluno
from model.frequencia import Frequencia


class ControllerFrequencia:
    """CRUD da coleção FREQUENCIA no MongoDB."""

    @staticmethod
    def _converter_data_hora(valor):
        """Valida a data/hora no formato AAAA-MM-DD HH:MM[:SS]."""
        for formato in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                return datetime.strptime(valor.strip(), formato)
            except (ValueError, TypeError, AttributeError):
                continue
        raise ValueError(
            "Data/hora inválida. Use o formato AAAA-MM-DD HH:MM."
        )

    @staticmethod
    def _validar_aluno(banco, id_aluno):
        """Verifica se o aluno existe."""
        if banco["aluno"].find_one({"id_aluno": id_aluno}) is None:
            raise ValueError("Aluno não encontrado.")

    @staticmethod
    def _documento_para_tupla(documento):
        """Converte um documento MongoDB para o formato da C2."""
        if documento is None:
            return None

        return (
            documento.get("id_frequencia"),
            documento.get("id_aluno"),
            documento.get("data_hora_entrada")
        )

    def registrar_entrada(self, id_aluno, data_hora_entrada=None):
        """Registra a entrada de um aluno e retorna o ID."""
        id_aluno = int(id_aluno)
        data_hora = (
            self._converter_data_hora(data_hora_entrada)
            if data_hora_entrada else datetime.now()
        )

        mongo = MongoQueries()

        try:
            banco = mongo.conectar()
            colecao = banco["frequencia"]

            self._validar_aluno(banco, id_aluno)

            # Busca o maior ID para gerar o próximo
            ultimo = colecao.find_one(sort=[("id_frequencia", -1)])

            novo_id = int(ultimo["id_frequencia"]) + 1 if ultimo else 1

            colecao.insert_one({
                "id_frequencia": novo_id,
                "id_aluno": id_aluno,
                "data_hora_entrada": data_hora
            })

            return novo_id

        finally:
            mongo.fechar()

    def atualizar(self, id_frequencia, id_aluno, data_hora_entrada) -> bool:
        """Atualiza o aluno e a data/hora de uma frequência."""
        id_aluno = int(id_aluno)
        data_hora = self._converter_data_hora(data_hora_entrada)

        mongo = MongoQueries()

        try:
            banco = mongo.conectar()

            self._validar_aluno(banco, id_aluno)

            resultado = banco["frequencia"].update_one(
                {"id_frequencia": int(id_frequencia)},
                {"$set": {
                    "id_aluno": id_aluno,
                    "data_hora_entrada": data_hora
                }}
            )

            return resultado.matched_count > 0

        finally:
            mongo.fechar()

    def deletar(self, id_frequencia) -> bool:
        """Exclui uma frequência pelo ID."""
        mongo = MongoQueries()

        try:
            banco = mongo.conectar()

            resultado = banco["frequencia"].delete_one(
                {"id_frequencia": int(id_frequencia)}
            )

            return resultado.deleted_count > 0

        finally:
            mongo.fechar()

    def buscar_por_id(self, id_frequencia):
        """Busca uma frequência pelo ID."""
        mongo = MongoQueries()

        try:
            banco = mongo.conectar()

            documento = banco["frequencia"].find_one(
                {"id_frequencia": int(id_frequencia)}
            )

            return self._documento_para_tupla(documento)

        finally:
            mongo.fechar()

    def listar(self):
        """Lista as frequências com o nome do aluno, da mais recente."""
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
                {"$sort": {"data_hora_entrada": -1}}
            ]

            documentos = banco["frequencia"].aggregate(pipeline)

            return [
                (
                    doc.get("id_frequencia"),
                    doc["aluno"].get("nome_aluno"),
                    doc.get("data_hora_entrada")
                )
                for doc in documentos
            ]

        finally:
            mongo.fechar()

    def obter(self, id_frequencia):
        """Retorna um objeto Frequencia com o Aluno."""
        linha = self.buscar_por_id(id_frequencia)

        if not linha:
            return None

        aluno = ControllerAluno().obter(linha[1])

        if aluno is None:
            return None

        return Frequencia(linha[0], aluno, linha[2])

    def listar_por_aluno(self, id_aluno):
        """Lista as frequências de um aluno, da mais recente."""
        mongo = MongoQueries()

        try:
            banco = mongo.conectar()

            documentos = banco["frequencia"].find(
                {"id_aluno": int(id_aluno)}
            ).sort("data_hora_entrada", -1)

            return [
                (doc.get("id_frequencia"), doc.get("data_hora_entrada"))
                for doc in documentos
            ]

        finally:
            mongo.fechar()
