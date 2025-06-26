import json
from config.settings import DATAJSON_GENERATED_PATH

class JSONWriter:
    @staticmethod
    def write(data):
        with open(DATAJSON_GENERATED_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Archivo JSON guardado en: {DATAJSON_GENERATED_PATH}")
