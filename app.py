import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rds.rds_database import RDSDataBase  # Certifique-se de que o caminho está correto
from rds.rds_riot import RDSriot

# Modelos de entrada da API
class RiotDataBaseInput(BaseModel):
    puuid: str = None
    match_id:str = None
    method: str  # Novo parâmetro para escolher qual método chamar
    user_key: str

# Modelos de entrada da API
class RDSDataBaseInput(BaseModel):
    query_type: str  # Tipo de consulta: 'by_column_value' ou 'from_two_tables'
    table_name: str  # Necessário para 'by_column_value'
    column_name: str = None  # Necessário para 'by_column_value'
    column_value: str = None  # Necessário para 'by_column_value'
    table1: str = None  # Necessário para 'from_two_tables'
    table2: str = None  # Necessário para 'from_two_tables'
    join_field1: str = None  # Necessário para 'from_two_tables'
    join_field2: str = None  # Necessário para 'from_two_tables'
    user_key: str


app = FastAPI()

@app.get("/")
def verify():
    return {"message": "API Check"}

@app.get("/riotrun")
def retrieval(data: RiotDataBaseInput):
    try:
        # Inicializa a classe com os parâmetros fornecidos
        riot = RDSriot(puuid=data.puuid, match_id=data.match_id)

        if data.user_key == "common_pass": 
            # Seleciona qual método chamar com base no parâmetro "method"
            if data.method == "get_summoner_info":
                result = riot.get_summoner_info(data.puuid)
            elif data.method == "get_matchs":
                result = riot.get_matchs(data.puuid)
            elif data.method == "get_info_match":
                match_info, transformed_player_info = riot.get_info_matchs_v5_players(data.match_id)
                result = {
                    "match_info": match_info,
                    "transformed_player_info": transformed_player_info
                }
            else:
                raise HTTPException(status_code=400, detail="Método não encontrado. Atenção os métodos que podem ser usados são: \n1-'get_summoner_info' (precisa do puuid da Riot), \n2-'get_matchs' (precisa do puuid da Riot para encontrar as 10 mais recentes partidas do jogador) e \n3-'get_info_matchs_v5_jogadores' (precisa do match_id da Riot).")
        else:
            raise HTTPException(status_code=400, detail="Solicitação inválida.")

        return {"data": result}
    
    except Exception as e:
        # Retorna erro em caso de falha
        raise HTTPException(status_code=500, detail=f"Erro: {e}")

@app.get("/rdsrun")
def retrieval(data: RDSDataBaseInput):
    try:
        db = RDSDataBase(
            table_name=data.table_name
        )
        db.connect()
        if data.user_key == "common_pass": 
            if data.query_type == "by_column_value":
                # Busca por valor de uma coluna específica
                if not (data.column_name and data.column_value):
                    raise HTTPException(status_code=400, detail="column_name e column_value são necessários para busca por valor de coluna.")
                result = db.get_by_column_value(data.table_name, data.column_name, data.column_value)
            
            elif data.query_type == "from_two_tables":
                # Busca em duas tabelas com campos diferentes
                if not (data.table1 and data.table2 and data.join_field1 and data.join_field2):
                    raise HTTPException(status_code=400, detail="table1, table2, join_field1 e join_field2 são necessários para busca em duas tabelas.")
                result = db.get_from_two_tables(data.table1, data.table2, data.join_field1, data.join_field2)
            
            else:
                raise HTTPException(status_code=400, detail="Tipo de consulta inválido. Use 'by_column_value' ou 'from_two_tables'.")
        else:
            raise HTTPException(status_code=400, detail="Solicitação inválida.")

        db.close()
        return {"data": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {e}")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8501)
    # uvicorn.run("app:app")
