import requests

import translate

def translateGameInfo(game: dict, cfg):
    print(game)
    game['name'] = translate.translateText(game['name'], cfg)
    game['desc'] = translate.translateText(game['desc'], cfg)    
    print(f"번역된 게임 제목: {game['name']}")
    print(f"번역된 게임 설명: {game['desc']}")

def translateText(text, cfg):
    url = "https://api-free.deepl.com/v2/translate"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "auth_key": cfg.getDeepLApiKey(),
        "text": text,
        "source_lang": "EN",
        "target_lang": "KO"
    }
    
    response = requests.post(url, headers=headers, data=data)
    translated_text = response.json()["translations"][0]["text"]
    return translated_text
