import requests
from openai import OpenAI
import json
import re

with open('config.json') as jsonfile:
    CREDENTIALS = json.load(jsonfile)

riot_key = CREDENTIALS['riot_key']
api_key=CREDENTIALS['openai_api_key']

class RDSriot:
    def __init__(self, puuid: str, match_id:str):
        self.puuid = puuid
        self.match_id = match_id

    # Função para acessar a API da Riot Games e obter o JSON do jogador
    def get_summoner_info(self, puuid:str):
        url = f"https://br1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={riot_key}"
        response = requests.get(url)
        if response.status_code == 200:
            summoner_data = response.text
            json_data = self.transform_summoner_info(summoner_data=summoner_data)
            return json_data
        else:
            raise Exception(f"Erro na API da Riot: {response.status_code}")

    # Função para transformar o JSON usando a API da OpenAI com o modelo GPT-4
    def transform_summoner_info(self, summoner_data:str):
        client = OpenAI(api_key=api_key)
        # Montando a mensagem para gerar o novo JSON
        messages = [
            {"role": "system", "content": "Você é um assistente que formata JSONs."},
            {"role": "user", "content": f"Você vai receber um JSON com informações do jogador. Você retornará um novo JSON apenas com as informações 'profileIconId' e 'summonerLevel':\n\n{summoner_data}"}
        ]
        
        # Chamando a API da OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=100,
            temperature=0
        )
        json_data = json.loads(str(response.choices[0].message.content))
        # Retornando o JSON transformado
        return json_data
    

    def get_matchs(self, puuid:str):
        url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=10&api_key={riot_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro na API da Riot: {response.status_code}")
        

    def get_info_matchs_v5_players(self, match_id:str):
        url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={riot_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.text
            match_info_1 = data.split('"participants":[{"allInPings"')[0]
            match_info_2 = re.search(r'"platformId".*', data)[0]
            match_data = f"{match_info_1}{match_info_2}"
            match_data_json = json.loads(match_data)

            # Separar jogadores que iniciam com '{"allInPings":'
            trechos_jogadores = data.split('{"allInPings":')
            jogadores = []

            # Processa cada trecho (ignora o primeiro item vazio)
            for i, trecho in enumerate(trechos_jogadores[1:], 1):
                # Reconstrói o JSON do jogador e adiciona à lista
                jogador = f'{{" Jogador\n{i}: \nallInPings":{trecho.strip()}}}'             
                transform_player_info = self.transform_player_info(jogador)
                jogador = {
                    f"Jogador_{i}": transform_player_info  # Usando um dicionário com chave dinâmica para cada jogador
                }
                jogadores.append(jogador)

            # # Exibe os resultados
            # for transform_player_info in jogadores:
            #     print(transform_player_info)

            return match_data_json, jogadores
        else:
            raise Exception(f"Erro na API da Riot: {response.status_code}")
    
        # Função para transformar o JSON usando a API da OpenAI com o modelo GPT-4
    def transform_player_info(self, player_info:str):
        client = OpenAI(api_key=api_key)
        # Montando a mensagem para gerar o novo JSON
        prompt = f"""Você vai receber informações de jogador de um torneio de League of Legends. A partir dessas informações, retorne apenas as seguintes informações no JSON:

                    - puuid
                    - assists
                    - bountyGold
                    - champExperience
                    - champLevel
                    - championId
                    - championName
                    - damagePerMinute
                    - damageTakenOnTeamPercentage;
                    - deaths
                    - dragonTakedowns
                    - individualPosition
                    - kda
                    - killParticipation
                    - kills
                    - lane
                    - riotIdGameName
                    - riotIdTagline
                    - role
                    - teamBaronKills
                    - teamElderDragonKills
                    - teamPosition
                    - win

                    Informações do Jogador:
                    {player_info}

                    Retorne essas informações em formato JSON, utilizando chaves e formato chave e valor (e.g. 'puuid': 'xx', 'assists': 'x').

                    """

        messages = [
            {"role": "system", "content": "Você é um assistente que formata JSONs."},
            {"role": "user", "content": prompt}
        ]
        
        # Chamando a API da OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=350,
            temperature=0
        )
        json_data_player = json.loads(str(response.choices[0].message.content))
        # Retornando o JSON transformado
        return json_data_player
    

