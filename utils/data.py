import json


def is_json_and_type(myjson: str, expected_type: type) -> bool:
    try:
        obj = json.loads(myjson)
        return isinstance(obj, expected_type)
    except ValueError:
        return False
