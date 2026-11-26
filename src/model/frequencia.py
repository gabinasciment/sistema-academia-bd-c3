
from datetime import datetime


class Frequencia:
    def __init__(self, id_frequencia, aluno, data_hora_entrada=None):
        self.id_frequencia = id_frequencia
        self.aluno = aluno
        self.data_hora_entrada = (
            data_hora_entrada if data_hora_entrada is not None
            else datetime.now()
        )

    # Consultar os atributos
    def get_id_frequencia(self):
        return self.id_frequencia

    def get_aluno(self):
        return self.aluno

    def get_data_hora_entrada(self):
        return self.data_hora_entrada

    # Alterar os atributos
    def set_id_frequencia(self, id_frequencia):
        self.id_frequencia = id_frequencia

    def set_aluno(self, aluno):
        self.aluno = aluno

    def set_data_hora_entrada(self, data_hora_entrada):
        self.data_hora_entrada = data_hora_entrada

    # Exibir as informacoes da frequencia
    def to_string(self):
        entrada = self.data_hora_entrada
        if hasattr(entrada, "strftime"):
            entrada = entrada.strftime("%d/%m/%Y %H:%M")
        return (
            f"ID: {self.id_frequencia} | "
            f"Aluno: {self.aluno.get_nome_aluno()} | "
            f"Entrada: {entrada}"
        )
