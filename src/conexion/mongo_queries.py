###########################################################################
# Modulo de conexao com o Banco de Dados MongoDB
#
# Adaptado do projeto de exemplo da disciplina
# (https://github.com/howardroatti/example_crud_mongo - Prof. Howard Roatti)
#
# Mudancas em relacao ao exemplo:
# - O arquivo de usuario/senha e encontrado a partir da pasta deste modulo,
#   igual ao oracle_queries.py.
# - O endereco do servidor pode vir da variavel de ambiente MONGO_HOST.
# - close() so fecha a conexao se ela estiver aberta.
###########################################################################

import os
from urllib.parse import quote_plus

import pymongo


# Pasta onde este arquivo esta (src/conexion)
PASTA_CONEXION = os.path.dirname(os.path.abspath(__file__))

ARQUIVO_AUTENTICACAO = os.path.join(
    PASTA_CONEXION,
    "passphrase",
    "authentication.mongo"
)


class MongoQueries:

    def __init__(self):
        # Na VM da disciplina o MongoDB roda na propria maquina (localhost).
        # Para acessar um MongoDB em outra maquina, defina a variavel de
        # ambiente MONGO_HOST com o IP dela, sem precisar alterar o codigo.
        self.host = os.environ.get("MONGO_HOST", "localhost")
        self.port = 27017
        self.database_name = "labdatabase"
        self.mongo_client = None
        self.db = None

        # O arquivo tem o formato: usuario,senha
        with open(ARQUIVO_AUTENTICACAO, "r") as f:
            self.user, self.passwd = f.read().strip().split(",")

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def connect(self):
        """
        Abre a conexao com o MongoDB e seleciona o banco labdatabase.
        quote_plus protege a senha caso ela tenha caracteres especiais.
        """
        self.mongo_client = pymongo.MongoClient(
            f"mongodb://{self.user}:{quote_plus(self.passwd)}"
            f"@{self.host}:{self.port}/"
        )
        self.db = self.mongo_client[self.database_name]

    def close(self):
        """
        Fecha a conexao, se estiver aberta.
        """
        if self.mongo_client is not None:
            self.mongo_client.close()
            self.mongo_client = None
            self.db = None
