#!/usr/bin/env python3
"""Import all Certamen round YAML files into the database defined by schema.sql."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

BASE_RAW_URL = "https://raw.githubusercontent.com/NJCL-Certamen/certamen-catalogue/refs/heads/main/questions"

def process_file(yaml_path: Path, path: str) -> dict[str, Any] | None:
    if not yaml_path.exists():
        print(f"YAML file not found: {yaml_path}", file=sys.stderr)
        return

    with yaml_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        print(f"The YAML file {yaml_path} must contain a top-level mapping.", file=sys.stderr)
        return
      
    return {
      "rel": f"{data.get('year')} {data.get('tournament')} {data.get('division')} {data.get('round')}",
      "href": f"{path}/{yaml_path.name}"
    }


def generate_contents(dir: Path, path: str) -> list[dict[str, Any]]:
    result = list()
    for item in dir.iterdir():
      if item.is_file():
        if item.name != "index.yaml":
          print(f"Processing file {item.name}", file=sys.stdout)
          file_result = process_file(item, path)
          if file_result is not None:
            result.append(file_result)
      elif item.is_dir():
        result += generate_contents(item, path + "/" + item.name)
        
    return result

def export_yaml(contents: list[dict[str, Any]]) -> int:
    contents_path = Path("questions/index.yaml")
    file_str = "links:\n"
    for link in contents:
      file_str += f"- rel: {link.get('rel')}\n"
      file_str += f"  href: {link.get('href')}\n"
    contents_path.write_text(file_str)
    return 0

def main() -> int:
    dir = Path("questions/")
    contents = generate_contents(dir, BASE_RAW_URL)
    return export_yaml(contents)


if __name__ == "__main__":
    sys.exit(main())
