import mysql.connector
from mysql.connector import Error
from fastapi import HTTPException
import json

with open('config.json') as jsonfile:
    CREDENTIALS = json.load(jsonfile)

class RDSDataBase:
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=CREDENTIALS["host"],
                port=CREDENTIALS["port"],
                user=CREDENTIALS["username"],
                password=CREDENTIALS["password"],
                database=CREDENTIALS["database"]  
            )
            return self.connection.is_connected()
        except Error as e:
            raise HTTPException(status_code=500, detail=f"Erro ao conectar ao banco de dados: {e}")

    def close(self):
        if self.connection.is_connected():
            self.connection.close()

    def execute_query(self, query: str, params=None):
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connect()
            cursor = self.connection.cursor()
            cursor.execute(query, params)  # Usar parâmetros para evitar injeções SQL
            return cursor.fetchall(), cursor.description  # Retorna também a descrição (nomes das colunas)
        except Error as e:
            raise HTTPException(status_code=500, detail=f"Erro ao executar a consulta: {e}")
        finally:
            cursor.close()

    def get_by_column_value(self, table_name: str, column_name: str, column_value: str):
        try:
            # Monta a query para buscar pelo valor de uma coluna específica
            query = f"SELECT * FROM `{table_name}` WHERE `{column_name}` = %s"  # Usando %s como placeholder
            result, description = self.execute_query(query, (column_value,))  # Passando o valor como parâmetro
            
            if result:
                column_names = [i[0] for i in description]  # Obtém os nomes das colunas
                record_dict = dict(zip(column_names, result[0]))  # Combina os nomes das colunas com os valores
                # Converte todos os valores em string
                for key in record_dict:
                    record_dict[key] = str(record_dict[key])
                return json.dumps(record_dict, ensure_ascii=False)  # Retorna o registro como JSON
            else:
                return json.dumps({"message": "Registro não encontrado."}, ensure_ascii=False)
        except Error as e:
            raise HTTPException(status_code=500, detail=f"Erro ao consultar registro: {e}")

    def get_from_two_tables(self, table1: str, table2: str, join_field1: str, join_field2: str):
        try:
            query = f"""
            SELECT * FROM `{table1}` t1
            JOIN `{table2}` t2 ON t1.{join_field1} = t2.{join_field2}
            """
            results, description = self.execute_query(query)
            
            column_names = [i[0] for i in description]  # Obtém os nomes das colunas
            records = [dict(zip(column_names, row)) for row in results]  # Combina colunas com os valores das linhas
            return json.dumps(records, ensure_ascii=False)
        except Error as e:
            raise HTTPException(status_code=500, detail=f"Erro ao realizar a consulta em duas tabelas: {e}")
