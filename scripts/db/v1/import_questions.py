#!/usr/bin/env python3
"""Import all Certamen round YAML files into the database defined by schema.sql."""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path
from typing import Any
from .import_yaml_to_db import import_yaml

import yaml

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.environ.get("SQL_HOST"))
    parser.add_argument("--port", default=os.environ.get("SQL_PORT"))
    parser.add_argument("--socket", default=os.environ.get("SQL_SOCKET"))
    parser.add_argument("--user", default=os.environ.get("SQL_USER"))
    parser.add_argument("--database", default=os.environ.get("SQL_DATABASE"))
    parser.add_argument("--password", default=os.environ.get("SQL_PASSWORD"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
        
    return 0


if __name__ == "__main__":
    sys.exit(main())
