#!/usr/bin/env python3
"""Read all question yaml files and check for unbalanced pseudo-tags"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml
import re

TAG_REGEX = r"<(latin|title|emphasis)>"

def check_tags(input: str) -> bool:
    match = re.search(TAG_REGEX, input)
    if match == None:
      return True
    
    close_tag = f"</{match.group(1)}>"
    try:
      end_index = input.index(close_tag, match.end())
    except ValueError:
      print(f"Invalid unclosed {match.group(1)} tag in {input}")
      return False

    if check_tags(input[match.end():end_index]) == False:
      return False
    
    if end_index + len(close_tag) >= len(input):
      return True
    else:
      return check_tags(input[end_index + len(close_tag):])

def process_file(file: Path) -> bool:
    if not file.exists():
        print(f"YAML file not found: {file}", file=sys.stderr)
        return False

    with file.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        print(f"The YAML file {file} must contain a top-level mapping.", file=sys.stderr)
        return False
      
    for question in list(data.get("questions") or []):
      if question.get("tossup") == None:
        print(f"Invalid format, missing tossup {question}")
        return False
      elif question.get("tossup").get("question") == None:
        print(f"Invalid format, missing tossup question {question.get('tossup')}")
        return False
      elif question.get("tossup").get("answer") == None:
        print(f"Invalid format, missing tossup answer {question.get('tossup')}")
        return False
      elif check_tags(question.get("tossup").get("question")) == False or check_tags(question.get("tossup").get("answer")) == False:
        return False
      
      for bonus in list(question.get("boni") or []):
        if bonus.get("question") == None:
          print(f"Invalid format, missing bonus question {bonus}")
          return False
        elif bonus.get("answer") == None:
          print(f"Invalid format, missing bonus answer {bonus}")
          return False
        elif check_tags(bonus.get("question")) == False or check_tags(bonus.get("answer")) == False:
          return False
    
    return True

def process_dir(dir: Path) -> bool:
    for item in dir.iterdir():
      if item.is_file():
        if item.name != "index.yaml":
          print(f"Processing file {item.name}", file=sys.stdout)
          if process_file(item) == False:
            print(f"Error in {item.name}")
            return False
      elif item.is_dir():
        if process_dir(item) == False:
          return False
    return True

def main() -> int:
    dir = Path("questions/")
    if process_dir(dir):
      return 0
    else:
      return 1


if __name__ == "__main__":
    sys.exit(main())
