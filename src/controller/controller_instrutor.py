
import re

from conexion.mongo_queries import MongoQueries
from model.instrutor import Instrutor


class ControllerInstrutor:
    """CRUD da coleção INSTRUTOR no MongoDB."""

    @staticmethod
    def _validar(nome, email, telefone):
        """Verifica se os campos obrigatórios foram informados."""
        if not nome or not nome.strip():
            raise ValueError("O nome do instrutor é obrigatório.")
        if not email or not email.strip():
            raise ValueError("O e-mail do instrutor é obrigatório.")
        if not telefone or not telefone.strip():
            raise ValueError("O telefone do instrutor é obrigatório.")

    @staticmethod
    def _documento_para_tupla(documento):
        """Converte um documento MongoDB para o formato da C2."""
        if documento is None:
            return None

        return (
            documento.get("id_instrutor"),
            documento.get("nome_instrutor"),
            documento.get("email_instrutor"),
            documento.get("telefone_instrutor")
        )

    def inserir(self, nome, email, telefone):
        """Insere um novo instrutor e retorna seu ID."""
        self._validar(nome, email, telefone)

        mongo = MongoQueries()

        try:
            banco = mongo.conectar()
            colecao = banco["instrutor"]

            # Evita cadastrar e-mails repetidos
            if self.existe_email(email):
                raise ValueError("Já existe um instrutor com esse e-mail.")

            # Busca o maior ID para gerar o próximo
            ultimo = colecao.find_one(sort=[("id_instrutor", -1)])

            novo_id = int(ultimo["id_instrutor"]) + 1 if ultimo else 1

            documento = {
                "id_instrutor": novo_id,
                "nome_instrutor": nome.strip(),
                "email_instrutor": email.strip(),
                "telefone_instrutor": telefone.strip()
            }

            colecao.insert_one(documento)

            return novo_id

        finally:
            mongo.fechar()

    def atualizar(self, id_instrutor, nome, email, telefone) -> bool:
        """Atualiza os dados de um instrutor."""
        self._validar(nome, email, telefone)

        mongo = MongoQueries()

        try:
            banco = mongo.conectar()

            if self.existe_email(email, ignorar_id=id_instrutor):
                raise ValueError("Já existe outro instrutor com esse e-mail.")

            resultado = banco["instrutor"].update_one(
                {"id_instrutor": int(id_instrutor)},
                {"$set": {
                    "nome_instrutor": nome.strip(),
                    "email_instrutor": email.strip(),
                    "telefone_instrutor": telefone.strip()
                }}
            )

            return resultado.matched_count > 0

        finally:
            mongo.fechar()

    def deletar(self, id_instrutor) -> bool:
        """Exclui um instrutor somente se não houver treinos dele."""
        id_instrutor = int(id_instrutor)

        mongo = MongoQueries()

        try:
            banco = mongo.conectar()

            if banco["treino"].count_documents(
                {"id_instrutor": id_instrutor}
            ) > 0:
                return False

            resultado = banco["instrutor"].delete_one(
                {"id_instrutor": id_instrutor}
            )

            return resultado.deleted_count > 0

        finally:
            mongo.fechar()

    def buscar_por_id(self, id_instrutor):
        """Busca um instrutor pelo ID."""
        mongo = MongoQueries()

        try:
            banco = mongo.conectar()

            documento = banco["instrutor"].find_one(
                {"id_instrutor": int(id_instrutor)}
            )

            return self._documento_para_tupla(documento)

        finally:
            mongo.fechar()

    def listar(self):
        """Lista os instrutores em ordem alfabética."""
        mongo = MongoQueries()

        try:
            banco = mongo.conectar()

            documentos = banco["instrutor"].find().sort("nome_instrutor", 1)

            return [
                self._documento_para_tupla(documento)
                for documento in documentos
            ]

        finally:
            mongo.fechar()

    def obter(self, id_instrutor):
        """Busca o instrutor e retorna um objeto Instrutor."""
        linha = self.buscar_por_id(id_instrutor)

        if not linha:
            return None

        return Instrutor(linha[0], linha[1], linha[2], linha[3])

    def existe_email(self, email, ignorar_id=None) -> bool:
        """Verifica se um e-mail já está cadastrado."""
        mongo = MongoQueries()

        try:
            banco = mongo.conectar()

            filtro = {
                "email_instrutor": {
                    "$regex": "^" + re.escape(email.strip()) + "$",
                    "$options": "i"
                }
            }

            if ignorar_id is not None:
                filtro["id_instrutor"] = {"$ne": int(ignorar_id)}

            return banco["instrutor"].count_documents(filtro) > 0

        finally:
            mongo.fechar()

    def contar_treinos(self, id_instrutor) -> int:
        """Conta os treinos orientados pelo instrutor."""
        mongo = MongoQueries()

        try:
            banco = mongo.conectar()

            return banco["treino"].count_documents(
                {"id_instrutor": int(id_instrutor)}
            )

        finally:
            mongo.fechar()

    def deletar_com_treinos(self, id_instrutor) -> bool:
        """Exclui os treinos do instrutor e depois o instrutor."""
        mongo = MongoQueries()

        try:
            banco = mongo.conectar()
            id_instrutor = int(id_instrutor)

            # Confirma se o instrutor existe
            if banco["instrutor"].find_one(
                {"id_instrutor": id_instrutor}
            ) is None:
                return False

            # Exclui os registros relacionados
            banco["treino"].delete_many({"id_instrutor": id_instrutor})

            # Exclui o instrutor
            resultado = banco["instrutor"].delete_one(
                {"id_instrutor": id_instrutor}
            )

            return resultado.deleted_count > 0

        finally:
            mongo.fechar()
