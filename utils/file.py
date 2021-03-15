from json import load,  dump
from typing import Any, Dict
from os import path


def read_json(name: str) -> Dict[str, Any]:
  if not path.exists(name):
    write_json(name, {})
    return {}
  file = open(name, 'r', encoding='utf-8')
  return load(file)


def write_json(name: str, data: Dict[str, Any]) -> None:
  dump(data, open(name,
                  'w+', encoding='utf-8'), ensure_ascii=False, indent=2)
