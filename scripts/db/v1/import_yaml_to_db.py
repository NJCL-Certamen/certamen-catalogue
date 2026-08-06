#!/usr/bin/env python3
"""Import a Certamen round YAML file into the database defined by schema.sql."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


def make_id(*parts: Any) -> str:
    payload = "|".join(str(part) for part in parts)
    return hashlib.md5(payload.encode("utf-8")).hexdigest()


def sql_literal(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace("'", "''")
        return "N'" + escaped + "'"
    return sql_literal(str(value))

def check_if_tournament_exists(tournament: str, args: argparse.Namespace) -> str | None:
    sql = f"SELECT id FROM tournament WHERE tournament_name = {sql_literal(tournament)};"
    
    cmd = ["mysql", f"--host={args.host}", f"--port={args.port}", f"--user={args.user}", f"--database={args.database}"]
    if args.socket:
        cmd.append(f"--socket={args.socket}")
    if args.password:
        cmd.append(f"--password={args.password}")
    
    completed = subprocess.run(
        cmd,
        input=sql,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    
    result = completed.stdout.strip()
    return result if result else None

def build_insert_sql(data: dict[str, Any], args: argparse.Namespace) -> str:
    tournament_name = str(data.get("tournament") or "").strip()
    year = str(data.get("year") or "")
    round_name = str(data.get("round") or "")
    questions = data.get("questions") or []

    statements: list[str] = []
    tournament_id = check_if_tournament_exists(tournament_name, args)
    if tournament_id is None:
      tournament_id = make_id("tournament", tournament_name)
      statements.append(
          "INSERT INTO tournament (id, tournament_name) "
          f"VALUES ({sql_literal(tournament_id)}, {sql_literal(tournament_name)}) "
          "ON DUPLICATE KEY UPDATE tournament_name = VALUES(tournament_name);"
      )
    round_id = make_id("round", tournament_name, year, round_name)


    statements.append(
        "INSERT INTO round (id, round, year, tournament_id) "
        f"VALUES ({sql_literal(round_id)}, {sql_literal(round_name)}, {sql_literal(year)}, {sql_literal(tournament_id)}) "
        "ON DUPLICATE KEY UPDATE round = VALUES(round), year = VALUES(year), tournament_id = VALUES(tournament_id);"
    )

    for index, item in enumerate(questions, start=1):
        tossup_data = item.get("tossup") or {}
        question = tossup_data.get("question")
        answer = tossup_data.get("answer")
        tossup_id = make_id("tossup", round_id, index)

        statements.append(
            "INSERT INTO tossup (id, question, answer, round_id, question_number) "
            f"VALUES ({sql_literal(tossup_id)}, {sql_literal(question)}, {sql_literal(answer)}, {sql_literal(round_id)}, {sql_literal(index)}) "
            "ON DUPLICATE KEY UPDATE question = VALUES(question), answer = VALUES(answer), round_id = VALUES(round_id), question_number = VALUES(question_number);"
        )

        boni = item.get("boni") or []
        for bonus_index, bonus in enumerate(boni, start=1):
            statements.append(
                "INSERT INTO bonus (tossup_id, bonus_number, question, answer) "
                f"VALUES ({sql_literal(tossup_id)}, {sql_literal(bonus_index)}, {sql_literal(bonus.get('question'))}, {sql_literal(bonus.get('answer'))}) "
                "ON DUPLICATE KEY UPDATE question = VALUES(question), answer = VALUES(answer);"
            )

    return "\n".join(statements)

def run_sql(sql: str, args: argparse.Namespace) -> None:
    cmd = ["mysql", f"--host={args.host}", f"--port={args.port}", f"--user={args.user}", f"--database={args.database}"]
    if args.socket:
        cmd.append(f"--socket={args.socket}")
    if args.password:
        cmd.append(f"--password={args.password}")

    completed = subprocess.run(
        cmd,
        input=sql,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "MySQL import failed.\n"
            f"Command: {' '.join(cmd)}\n"
            f"stdout: {completed.stdout}\n"
            f"stderr: {completed.stderr}"
        )

def import_yaml(yaml_path: Path, args: argparse.Namespace) -> bool:
    if not yaml_path.exists():
        print(f"YAML file not found: {yaml_path}", file=sys.stderr)
        return False

    with yaml_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        print(f"The YAML file {yaml_path} must contain a top-level mapping.", file=sys.stderr)
        return False

    sql = build_insert_sql(data)
    run_sql(sql, args)
    print(f"Imported {len(data.get('questions') or [])} tossups from {yaml_path.name}.")
    return True
