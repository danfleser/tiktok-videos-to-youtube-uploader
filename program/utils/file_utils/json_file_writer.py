import io
import json


def write_json_file(json_file_path, data):
    with io.open(json_file_path, 'w', encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
