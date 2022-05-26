import json
from typing import List, Union

def __append_json_extension(name: str) -> str:
    import re
    p = re.compile('\.json$')
    if not p.search(name):
        name += '.json'
    return name

def save_json_as_file(data: Union[dict, List[dict]], file_path: str) -> None:
    with open(__append_json_extension(file_path), 'w') as file:
        json.dump(data, file, ensure_ascii=False)

def read_json_by_file_path(file_path: str) -> Union[dict, List[dict]]:
    with open(__append_json_extension(file_path), 'r') as file:
        return json.load(file)
