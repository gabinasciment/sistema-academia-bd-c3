# Prompts desenvolvidos ao longo do projeto

## Prompt 1 — Migração do Oracle para o MongoDB (Esther)

"A partir do projeto da C2 (tabelas ALUNO, INSTRUTOR, TREINO e FREQUENCIA no Oracle) e do item 4 do edital da C3, me ajude a entender os conceitos do MongoDB (coleção, documento e índice único) e a montar, seguindo o projeto de exemplo do professor (example_crud_mongo), a conexão com o MongoDB e o script que lê as tabelas do Oracle e cria as coleções com os mesmos nomes e os documentos com os registros, deixando o projeto o mais parecido possível com o da C2."

**Fonte:** Claude Code (Anthropic).

Usei a ferramenta como apoio para estudar as diferenças entre o Oracle e o MongoDB e para gerar uma primeira versão dos códigos a partir dos arquivos da C2 e do exemplo do professor. Ela também instalou o MongoDB no meu computador e criou o usuário `labdatabase`, igual ao da VM. Revisei cada etapa do script, que segue a ordem do item 4 do edital (conecta ao Oracle, consulta as tabelas, conecta ao MongoDB, cria as coleções e insere os documentos), e mantive os nomes dos campos iguais às colunas da C2, os IDs como números e as datas como datas. Nos testes no meu computador, as quatro coleções ficaram com o mesmo número de registros das tabelas (10 alunos, 4 instrutores, 20 treinos e 30 frequências), o script pôde ser executado de novo sem duplicar os dados e o índice único bloqueou e-mails repetidos.
