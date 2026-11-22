
import os
from pymongo import MongoClient


class MongoQueries:
    def __init__(self):
        usuario = os.environ.get("MONGO_USER")
        senha = os.environ.get("MONGO_PASSWORD")

        if not usuario or not senha:
            raise ValueError(
                "Configure MONGO_USER e MONGO_PASSWORD."
            )

        self.client = MongoClient(
            host="localhost",
            port=27017,
            username=usuario,
            password=senha,
            authSource="admin",
            serverSelectionTimeoutMS=5000
        )

        self.db = self.client["sistema_academia"]

    def conectar(self):
        self.client.admin.command("ping")
        return self.db

    def fechar(self):
        self.client.close()

