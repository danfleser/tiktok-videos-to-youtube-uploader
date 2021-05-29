import io
import json


def load_json_file(json_file_path):
    with io.open(json_file_path, 'r', encoding="utf-8") as file:
        data = json.load(file)

    return data
