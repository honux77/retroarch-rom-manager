import requests

import translate
from config import Config

def translateGameInfo(game: dict):
    
    config = Config()
    print(game)
    game['name'] = translate.translateText(game['name'], config)
    game['desc'] = translate.translateText(game['desc'], config)    
    print(f"번역된 게임 제목: {game['name']}")
    print(f"번역된 게임 설명: {game['desc']}")

def translateText(text, config):
    url = "https://api-free.deepl.com/v2/translate"

    api_key = config.getDeepLApiKey()
    if api_key is None:
        print("DeepL API 키가 설정되지 않았습니다. secret.ini 파일을 확인하세요.")
        return text

    # 2025년 11월부터 헤더 기반 인증 필수
    headers = {
        "Authorization": f"DeepL-Auth-Key {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "text": [text],
        "source_lang": "EN",
        "target_lang": "KO"
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()

        if "translations" in response_json:
            translated_text = response_json["translations"][0]["text"]
            return translated_text
        else:
            print(f"DeepL API 오류: {response_json}")
            return text
    except Exception as e:
        print(f"번역 중 오류 발생: {e}")
        return text
