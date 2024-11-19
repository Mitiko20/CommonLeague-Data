import os
import json
import requests


## Teste para consulta de tabela RDS

# URL do endpoint de recuperação de dados

# URL = "http://0.0.0.0:8501/rdsrun"
# URL = "http://15.228.252.158:8501/rdsrun"
# headers = {'Content-Type': 'application/json'}

# # Payload com as informações para acessar o banco MySQL e a tabela
# payload = json.dumps(
#     {
#         "table_name": "users_p2",  # Nome da tabela
#         "query_type": "by_column_value",  
#         "column_name": "user_id",
#         "column_value": "0142f69a-4127-47fc-ba0a-aa1fa2defeca"
#     }
# )

# # Fazendo a requisição POST para o endpoint /run
# response = requests.post(URL, headers=headers, data=payload, verify=False)

# # Mostrando o resultado
# result = response.text.replace("\\", "")
# print(result)

# Teste para RIOT
# URL do endpoint de recuperação de dados
URL = "http://0.0.0.0:8501/riotrun"
# URL = "http://15.228.252.158:8501/riotrun"
headers = {'Content-Type': 'application/json'}

# Payload com as informações para acessar o banco MySQL e a tabela
payload = json.dumps(
    {
        "match_id":"BR1_2930788372",
        "puuid": "_-qSsd2yeqbtiQiff6UMa--BOTxqdvOfKgTOIPdvNwxEpiA7LR1TpwCXOZ1MoqEfEGdINtbn5I20CQ",
        "method":"get_matchs",
        "user_key":"common_pass",
    }
)

# Fazendo a requisição POST para o endpoint /run
response = requests.get(URL, headers=headers, data=payload, verify=False)

# Mostrando o resultado
result = response.text
print(result)