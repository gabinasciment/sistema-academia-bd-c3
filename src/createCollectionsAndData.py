# Cria as colecoes do Sistema de Academia no MongoDB a partir das tabelas
# do Oracle da C2 (edital da C3, item 4).
# Como rodar (dentro da pasta src): python3 createCollectionsAndData.py
#
# As tabelas do Oracle precisam existir e ter os registros. Se ainda nao
# tiverem, rode antes: python3 create_tables_and_records.py
#
# Etapas do edital (item 4):
#   I.   conecta ao Oracle
#   II.  consulta cada tabela da C2
#   III. conecta ao MongoDB
#   IV.  cria uma colecao com o mesmo nome de cada tabela
#   V.   cria os documentos com os registros de cada tabela
#
# Pode ser executado quantas vezes quiser: as colecoes sao apagadas e
# criadas de novo, como o script SQL da C2 faz com as tabelas.
from conexion.oracle_queries import OracleQueries
from conexion.mongo_queries import MongoQueries

# Mesmos nomes das tabelas da C2 (edital, item 4.IV)
COLECOES = ["aluno", "instrutor", "treino", "frequencia"]

# Campos que nao podem se repetir, como o UNIQUE dos e-mails nas tabelas da C2
CAMPOS_UNICOS = {
    "aluno": "email_aluno",
    "instrutor": "email_instrutor",
}


def criar_colecoes(mongo: MongoQueries):
    '''
    IV. Cria uma colecao para cada tabela. Se ela ja existir, e apagada
    antes, para comecar do zero. Depois cria os indices unicos dos e-mails.
    '''
    existentes = mongo.db.list_collection_names()

    for colecao in COLECOES:
        if colecao in existentes:
            mongo.db.drop_collection(colecao)
        mongo.db.create_collection(colecao)
        print(f"Colecao {colecao} criada")

    for colecao, campo in CAMPOS_UNICOS.items():
        mongo.db[colecao].create_index(campo, unique=True)
        print(f"Indice unico criado em {colecao}.{campo}")


def migrar_registros(oracle: OracleQueries, mongo: MongoQueries):
    '''
    II e V. Le cada tabela do Oracle e insere um documento para cada linha.
    Os campos ficam com os mesmos nomes das colunas (em minusculas), os IDs
    continuam numeros e as datas continuam datas, como na C2.
    '''
    for colecao in COLECOES:
        df = oracle.sqlToDataFrame(f"select * from {colecao} order by 1")  # II
        documentos = df.to_dict("records")  # cada linha vira um documento

        if documentos:
            mongo.db[colecao].insert_many(documentos)  # V
        print(f"{len(documentos)} documentos inseridos em {colecao}")


def mostrar_totais(mongo: MongoQueries):
    print("\nTOTAL DE DOCUMENTOS POR COLECAO")
    for colecao in COLECOES:
        total = mongo.db[colecao].count_documents({})
        print(f"  {colecao.upper():<12} {total}")


def run():
    oracle = OracleQueries()
    oracle.connect()  # I

    mongo = MongoQueries()
    mongo.connect()  # III

    try:
        print("Criando colecoes...\n")
        criar_colecoes(mongo)

        print("\nCopiando os registros do Oracle para o MongoDB...\n")
        migrar_registros(oracle, mongo)

        mostrar_totais(mongo)
    finally:
        mongo.close()
        oracle.close()


if __name__ == '__main__':
    run()
