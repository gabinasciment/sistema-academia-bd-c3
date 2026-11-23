
from datetime import datetime

from conexion.mongo_queries import MongoQueries
from model.aluno import Aluno


class ControllerAluno:
    """CRUD da coleção ALUNO no MongoDB."""

    @staticmethod
    def _converter_data(data_nascimento):
        """Valida a data no formato AAAA-MM-DD."""
        try:
            return datetime.strptime(
                data_nascimento, "%Y-%m-%d"
            ).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            raise ValueError(
                "Data inválida. Use o formato AAAA-MM-DD."
            )

    @staticmethod
    def _validar(nome):
        """Verifica se o nome do aluno foi informado."""
        if not nome or not nome.strip():
            raise ValueError("O nome do aluno é obrigatório.")

    @staticmethod
    def _documento_para_tupla(documento):
        """Converte um documento MongoDB para o formato da C2."""
        if documento is None:
            return None

        return (
            documento.get("id_aluno"),
            documento.get("nome_aluno"),
            documento.get("email_aluno"),
            documento.get("telefone_aluno"),
            documento.get("data_nascimento"),
            documento.get("genero")
        )

    def inserir(self, nome, email, telefone,
                data_nascimento, genero):
        """Insere um novo aluno e retorna seu ID."""
        self._validar(nome)

        mongo = MongoQueries()

        try:
            banco = mongo.conectar()
            colecao = banco["aluno"]

            # Evita cadastrar e-mails repetidos
            if self.existe_email(email):
                raise ValueError(
                    "Já existe um aluno com esse e-mail."
                )

            # Busca o maior ID para gerar o próximo
            ultimo_aluno = colecao.find_one(
                sort=[("id_aluno", -1)]
            )

            novo_id = (
                int(ultimo_aluno["id_aluno"]) + 1
                if ultimo_aluno else 1
            )

            documento = {
                "id_aluno": novo_id,
                "nome_aluno": nome.strip(),
                "email_aluno": email.strip(),
                "telefone_aluno": telefone.strip(),
                "data_nascimento": self._converter_data(
                    data_nascimento
                ),
                "genero": genero.strip()
            }

            colecao.insert_one(documento)

            return novo_id

        finally:
            mongo.fechar()

    def atualizar(self, id_aluno, nome, email, telefone,
                  data_nascimento, genero) -> bool:
        """Atualiza os dados de um aluno."""
        self._validar(nome)

        mongo = MongoQueries()

        try:
            banco = mongo.conectar()
            colecao = banco["aluno"]

            if self.existe_email(email, ignorar_id=id_aluno):
                raise ValueError(
                    "Já existe outro aluno com esse e-mail."
                )

            novos_dados = {
                "nome_aluno": nome.strip(),
                "email_aluno": email.strip(),
                "telefone_aluno": telefone.strip(),
                "data_nascimento": self._converter_data(
                    data_nascimento
                ),
                "genero": genero.strip()
            }

            resultado = colecao.update_one(
                {"id_aluno": int(id_aluno)},
                {"$set": novos_dados}
            )

            return resultado.matched_count > 0

        finally:
            mongo.fechar()

    def deletar(self, id_aluno) -> bool:
        """Exclui um aluno somente se não houver dependentes."""
        id_aluno = int(id_aluno)

        mongo = MongoQueries()

        try:
            banco = mongo.conectar()
            colecao = banco["aluno"]

            treinos = banco["treino"].count_documents(
                {"id_aluno": id_aluno}
            )

            frequencias = banco["frequencia"].count_documents(
                {"id_aluno": id_aluno}
            )

            if treinos > 0 or frequencias > 0:
                return False

            resultado = colecao.delete_one(
                {"id_aluno": id_aluno}
            )

            return resultado.deleted_count > 0

        finally:
            mongo.fechar()

    def buscar_por_id(self, id_aluno):
        """Busca um aluno pelo ID."""
        mongo = MongoQueries()

        try:
            banco = mongo.conectar()

            documento = banco["aluno"].find_one(
                {"id_aluno": int(id_aluno)}
            )

            return self._documento_para_tupla(documento)

        finally:
            mongo.fechar()

    def listar(self):
        """Lista os alunos em ordem alfabética."""
        mongo = MongoQueries()

        try:
            banco = mongo.conectar()

            documentos = banco["aluno"].find().sort(
                "nome_aluno", 1
            )

            return [
                self._documento_para_tupla(documento)
                for documento in documentos
            ]

        finally:
            mongo.fechar()

    def obter(self, id_aluno):
        """Busca o aluno e retorna um objeto Aluno."""
        linha = self.buscar_por_id(id_aluno)

        if not linha:
            return None

        return Aluno(
            linha[0],
            linha[1],
            linha[2],
            linha[3],
            linha[4],
            linha[5]
        )

    def existe_email(self, email, ignorar_id=None) -> bool:
        """Verifica se um e-mail já está cadastrado."""
        mongo = MongoQueries()

        try:
            banco = mongo.conectar()
            colecao = banco["aluno"]

            filtro = {
                "email_aluno": {
                    "$regex": "^" + __import__("re").escape(
                        email.strip()
                    ) + "$",
                    "$options": "i"
                }
            }

            if ignorar_id is not None:
                filtro["id_aluno"] = {
                    "$ne": int(ignorar_id)
                }

            return colecao.count_documents(filtro) > 0

        finally:
            mongo.fechar()

    def contar_dependentes(self, id_aluno):
        """Conta treinos e frequências relacionados ao aluno."""
        mongo = MongoQueries()

        try:
            banco = mongo.conectar()
            id_aluno = int(id_aluno)

            treinos = banco["treino"].count_documents(
                {"id_aluno": id_aluno}
            )

            frequencias = banco["frequencia"].count_documents(
                {"id_aluno": id_aluno}
            )

            return treinos, frequencias

        finally:
            mongo.fechar()

    def deletar_com_dependentes(self, id_aluno) -> bool:
        """Exclui os dependentes e depois o aluno."""
        mongo = MongoQueries()

        try:
            banco = mongo.conectar()
            id_aluno = int(id_aluno)

            # Confirma se o aluno existe
            aluno = banco["aluno"].find_one(
                {"id_aluno": id_aluno}
            )

            if aluno is None:
                return False

            # Exclui registros relacionados
            banco["treino"].delete_many(
                {"id_aluno": id_aluno}
            )

            banco["frequencia"].delete_many(
                {"id_aluno": id_aluno}
            )

            # Exclui o aluno
            resultado = banco["aluno"].delete_one(
                {"id_aluno": id_aluno}
            )

            return resultado.deleted_count > 0

        finally:
            mongo.fechar()
