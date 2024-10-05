import requests

import translate
from config import Config

def translateGameInfo(game: dict):
    
    config = Config()
    print(game)
    game['name'] = translate.translateText(game['name'], cconfigfg)
    game['desc'] = translate.translateText(game['desc'], config)    
    print(f"번역된 게임 제목: {game['name']}")
    print(f"번역된 게임 설명: {game['desc']}")

def translateText(text, config):
    url = "https://api-free.deepl.com/v2/translate"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "auth_key": config.getDeepLApiKey(),
        "text": text,
        "source_lang": "EN",
        "target_lang": "KO"
    }
    
    response = requests.post(url, headers=headers, data=data)
    translated_text = response.json()["translations"][0]["text"]
    return translated_text
