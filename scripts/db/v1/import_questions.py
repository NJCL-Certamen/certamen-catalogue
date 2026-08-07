#!/usr/bin/env python3
"""Import all Certamen round YAML files into the database defined by schema.sql."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any
from import_yaml_to_db import import_yaml

import yaml

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.environ.get("CERTAMEN_SQL_HOST"))
    parser.add_argument("--port", default=os.environ.get("CERTAMEN_SQL_PORT"))
    parser.add_argument("--socket", default=os.environ.get("CERTAMEN_SQL_SOCKET"))
    parser.add_argument("--user", default=os.environ.get("CERTAMEN_SQL_USER"))
    parser.add_argument("--database", default=os.environ.get("CERTAMEN_SQL_DATABASE"))
    parser.add_argument("--password", default=os.environ.get("CERTAMEN_SQL_PASSWORD"))
    return parser.parse_args()

def process_dir(dir: Path, args) -> None:
    for item in dir.iterdir():
      if item.is_file():
        if item.name != "index.yaml":
          print(f"Processing file {item.name}", file=sys.stdout)
          import_yaml(item, args)
      elif item.is_dir():
        process_dir(item, args)

def main() -> int:
    args = parse_args()
    
    dir = Path("questions/")
    process_dir(dir, args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
