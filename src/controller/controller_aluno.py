
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
            documento.get("ID_ALUNO"),
            documento.get("NOME_ALUNO"),
            documento.get("EMAIL_ALUNO"),
            documento.get("TELEFONE_ALUNO"),
            documento.get("DATA_NASCIMENTO"),
            documento.get("GENERO")
        )

    def inserir(self, nome, email, telefone,
                data_nascimento, genero):
        """Insere um novo aluno e retorna seu ID."""
        self._validar(nome)

        mongo = MongoQueries()

        try:
            banco = mongo.conectar()
            colecao = banco["ALUNO"]

            # Evita cadastrar e-mails repetidos
            if self.existe_email(email):
                raise ValueError(
                    "Já existe um aluno com esse e-mail."
                )

            # Busca o maior ID para gerar o próximo
            ultimo_aluno = colecao.find_one(
                sort=[("ID_ALUNO", -1)]
            )

            novo_id = (
                int(ultimo_aluno["ID_ALUNO"]) + 1
                if ultimo_aluno else 1
            )

            documento = {
                "ID_ALUNO": novo_id,
                "NOME_ALUNO": nome.strip(),
                "EMAIL_ALUNO": email.strip(),
                "TELEFONE_ALUNO": telefone.strip(),
                "DATA_NASCIMENTO": self._converter_data(
                    data_nascimento
                ),
                "GENERO": genero.strip()
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
            colecao = banco["ALUNO"]

            if self.existe_email(email, ignorar_id=id_aluno):
                raise ValueError(
                    "Já existe outro aluno com esse e-mail."
                )

            novos_dados = {
                "NOME_ALUNO": nome.strip(),
                "EMAIL_ALUNO": email.strip(),
                "TELEFONE_ALUNO": telefone.strip(),
                "DATA_NASCIMENTO": self._converter_data(
                    data_nascimento
                ),
                "GENERO": genero.strip()
            }

            resultado = colecao.update_one(
                {"ID_ALUNO": int(id_aluno)},
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
            colecao = banco["ALUNO"]

            treinos = banco["TREINO"].count_documents(
                {"ID_ALUNO": id_aluno}
            )

            frequencias = banco["FREQUENCIA"].count_documents(
                {"ID_ALUNO": id_aluno}
            )

            if treinos > 0 or frequencias > 0:
                return False

            resultado = colecao.delete_one(
                {"ID_ALUNO": id_aluno}
            )

            return resultado.deleted_count > 0

        finally:
            mongo.fechar()

    def buscar_por_id(self, id_aluno):
        """Busca um aluno pelo ID."""
        mongo = MongoQueries()

        try:
            banco = mongo.conectar()

            documento = banco["ALUNO"].find_one(
                {"ID_ALUNO": int(id_aluno)}
            )

            return self._documento_para_tupla(documento)

        finally:
            mongo.fechar()

    def listar(self):
        """Lista os alunos em ordem alfabética."""
        mongo = MongoQueries()

        try:
            banco = mongo.conectar()

            documentos = banco["ALUNO"].find().sort(
                "NOME_ALUNO", 1
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
            colecao = banco["ALUNO"]

            filtro = {
                "EMAIL_ALUNO": {
                    "$regex": "^" + __import__("re").escape(
                        email.strip()
                    ) + "$",
                    "$options": "i"
                }
            }

            if ignorar_id is not None:
                filtro["ID_ALUNO"] = {
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

            treinos = banco["TREINO"].count_documents(
                {"ID_ALUNO": id_aluno}
            )

            frequencias = banco["FREQUENCIA"].count_documents(
                {"ID_ALUNO": id_aluno}
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
            aluno = banco["ALUNO"].find_one(
                {"ID_ALUNO": id_aluno}
            )

            if aluno is None:
                return False

            # Exclui registros relacionados
            banco["TREINO"].delete_many(
                {"ID_ALUNO": id_aluno}
            )

            banco["FREQUENCIA"].delete_many(
                {"ID_ALUNO": id_aluno}
            )

            # Exclui o aluno
            resultado = banco["ALUNO"].delete_one(
                {"ID_ALUNO": id_aluno}
            )

            return resultado.deleted_count > 0

        finally:
            mongo.fechar()
