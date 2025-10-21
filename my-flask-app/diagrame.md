[USUARIO] <-------------------+         +------------------< [AUDITORIA]
   | id (PK)                 |         | id (PK)
   | nome                    |         | usuario_id (FK)
   | email (único)           |         | acao
   | senha (criptografada)   |         | data_hora
   | cargo                   |         | ip
   | status                  |         | status
   | departamento            |
   | ultimo_acesso           |
   | rosto (imagem/biometria)|
   | criado_em               |
   |                         |
   +-------------------------+
             |
             | 1
             |
             v N
[FUNCIONARIO_TAREFA] >---+         +---< [TAREFA]
   | id (PK)             |         | id (PK)
   | funcionario_id (FK) |         | titulo
   | tarefa_id (FK)      |         | descricao
                         |         | status
                         |         | data_criacao
                         |         | data_conclusao
                         |         | gerente_id (FK para USUARIO)
                         |         | criado_em
                         +---------+

[USUARIO] 1 <------------------- N [PONTO]
   | id (PK)                      | id (PK)
   | ...                          | usuario_id (FK)
                                  | data
                                  | hora_entrada
                                  | hora_saida
                                  | total_horas
                                  | status
                                  | criado_em