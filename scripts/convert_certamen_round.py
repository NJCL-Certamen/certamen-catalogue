#!/usr/bin/env python3
"""Create reviewable YAML drafts from an RTF or plain-text Certamen source."""

from __future__ import annotations

import argparse
import codecs
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml
from striprtf.striprtf import PATTERN, destinations, specialchars


ROUND_RE = re.compile(
    r"^(?P<label>(?:ROUND\s+(?:ONE|TWO|THREE|FOUR|FIVE|\d+)|"
    r"SEMI[- ]FINAL(?:S)?|FINAL(?: ROUND)?|UPPER EXTRA QUESTIONS|"
    r"(?:NOVICE\s+)?EXTRA QUESTIONS))\b",
    re.IGNORECASE,
)
QUESTION_RE = re.compile(r"^\s*(?:TOSS[- ]?UP\s*)?(?P<number>\d+)[.):]\s*(?P<body>.*)$", re.IGNORECASE)
TOKEN_RE = re.compile(r"\S+")
TAG_RE = re.compile(r"</?(?:latin|title|emphasis)>")

ROUND_NAMES = {
    "ONE": "Round 1",
    "TWO": "Round 2",
    "THREE": "Round 3",
    "FOUR": "Round 4",
    "FIVE": "Round 5",
}


def read_source(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() != ".rtf":
        return raw
    return decode_rtf(raw)


def decode_rtf(raw: str) -> str:
    """Decode RTF text while retaining bold, italic, and underline runs."""
    state = {"bold": False, "italic": False, "underline": False}
    stack: list[tuple[dict[str, bool], bool, bool, int, int]] = []
    segments: list[tuple[str, tuple[bool, bool, bool]]] = []
    ignorable = False
    suppress_output = False
    ucskip = 1
    curskip = 0
    hex_buffer = ""
    encoding = "cp1252"

    def append(value: str) -> None:
        if value and not ignorable and not suppress_output:
            style = (state["bold"], state["italic"], state["underline"])
            if segments and segments[-1][1] == style:
                segments[-1] = (segments[-1][0] + value, style)
            else:
                segments.append((value, style))

    for match in PATTERN.finditer(raw):
        word, argument, hex_code, character, brace, text_character = match.groups()
        if hex_buffer and not hex_code:
            append(bytes.fromhex(hex_buffer).decode(encoding, errors="replace"))
            hex_buffer = ""
        if brace:
            curskip = 0
            if brace == "{":
                stack.append((state.copy(), ignorable, suppress_output, ucskip, curskip))
            else:
                if stack:
                    state, ignorable, suppress_output, ucskip, curskip = stack.pop()
            continue
        if character:
            curskip = 0
            if character == "*":
                ignorable = True
            elif character in specialchars:
                append(specialchars[character])
            continue
        if word:
            curskip = 0
            if word in destinations:
                ignorable = True
            if word == "ansicpg" and argument:
                candidate = f"cp{argument}"
                try:
                    codecs.lookup(candidate)
                    encoding = candidate
                except LookupError:
                    pass
            if word == "fonttbl" or word == "colortbl":
                suppress_output = True
            if word == "b":
                state["bold"] = argument != "0"
            elif word == "i":
                state["italic"] = argument != "0"
            elif word == "ul":
                state["underline"] = argument != "0"
            elif word in {"ulnone", "ul0"}:
                state["underline"] = False
            elif word == "plain":
                state = {"bold": False, "italic": False, "underline": False}
            elif word == "uc" and argument:
                ucskip = int(argument)
            elif word == "u" and argument:
                codepoint = int(argument)
                if codepoint < 0:
                    codepoint += 0x10000
                append(chr(codepoint))
                curskip = ucskip
            elif word in specialchars:
                append(specialchars[word])
            continue
        if hex_code:
            if curskip > 0:
                curskip -= 1
            elif not ignorable and not suppress_output:
                hex_buffer += hex_code
            continue
        if text_character:
            if curskip > 0:
                curskip -= 1
            else:
                append(text_character)

    if hex_buffer:
        append(bytes.fromhex(hex_buffer).decode(encoding, errors="replace"))

    characters: list[tuple[str, tuple[bool, bool, bool]]] = [
        (character, style) for value, style in segments for character in value
    ]
    for index in range(1, len(characters) - 1):
        character, style = characters[index]
        if character.isalpha() and not any(style):
            previous_index = index - 1
            while previous_index >= 0 and not characters[previous_index][0].isalpha():
                previous_index -= 1
            next_index = index + 1
            while next_index < len(characters) and not characters[next_index][0].isalpha():
                next_index += 1
            no_style = (False, False, False)
            previous_style = characters[previous_index][1] if previous_index >= 0 else no_style
            next_style = characters[next_index][1] if next_index < len(characters) else no_style
            if previous_style == next_style and any(previous_style):
                characters[index] = (character, previous_style)

    merged: list[tuple[str, tuple[bool, bool, bool]]] = []
    for character, style in characters:
        if merged and merged[-1][1] == style:
            merged[-1] = (merged[-1][0] + character, style)
        else:
            merged.append((character, style))

    output: list[str] = []
    for value, style in merged:
        bold, italic, underline = style
        if bold:
            value = f"<latin>{value}</latin>"
        if italic:
            value = f"<title>{value}</title>"
        if underline:
            value = f"<emphasis>{value}</emphasis>"
        output.append(value)
    return "".join(output)


def display_round(label: str) -> str:
    normalized = re.sub(r"\s+", " ", label.strip()).upper()
    match = re.search(r"ROUND\s+(ONE|TWO|THREE|FOUR|FIVE|\d+)", normalized)
    if match:
        value = match.group(1)
        return ROUND_NAMES.get(value, f"Round {value}")
    if "SEMI" in normalized:
        return "Semifinals"
    if "FINAL" in normalized:
        return "Finals"
    return "Extra Questions"


def split_sections(text: str) -> list[tuple[str, list[str]]]:
    sections: list[tuple[str, list[str]]] = []
    current_label: str | None = None
    current_lines: list[str] = []
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        plain_line = TAG_RE.sub("", line)
        if not line:
            continue
        match = ROUND_RE.match(plain_line)
        if match:
            if current_label is not None and match.group("label").casefold() == current_label.casefold():
                continue
            if current_label is not None:
                sections.append((current_label, current_lines))
            current_label = match.group("label")
            current_lines = []
        elif current_label is not None:
            current_lines.append(line)
    if current_label is not None:
        sections.append((current_label, current_lines))
    return sections


def question_blocks(lines: list[str]) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for line in lines:
        plain_line = TAG_RE.sub("", line)
        if re.match(
            r"^(?:(?:UPPER|NOVICE) (?:ROUND|SEMI|FINAL|EXTRA)|"
            r"GRAMMAR / VOCABULARY|HISTORY / LIFE / GEOGRAPHY|MYTHOLOGY|\d+\s*$)",
            plain_line,
            re.IGNORECASE,
        ):
            continue
        if QUESTION_RE.match(plain_line):
            if current:
                blocks.append(" ".join(current))
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append(" ".join(current))
    return blocks


def is_upper_answer_token(token: str) -> bool:
    token = TAG_RE.sub("", token)
    letters = "".join(character for character in token if character.isalpha())
    if not letters:
        return token in {"--", "/", "&", "+", "//"}
    if len(letters) == 1:
        cleaned = token.strip("\"'“”‘’()[]{}")
        return letters.isupper() and (cleaned.endswith(".") or cleaned == letters)
    return letters.isupper()


def normalize_tags(value: str) -> str:
    """Keep pseudo-tags balanced after splitting a formatted source block."""
    tag_pattern = re.compile(r"(<(/?)(latin|title|emphasis)>)")
    active: list[str] = []
    output: list[str] = []
    position = 0
    for match in tag_pattern.finditer(value):
        output.append(value[position:match.start()])
        tag_name = match.group(3)
        if match.group(2):
            if tag_name in active:
                active.remove(tag_name)
                output.append(match.group(1))
        else:
            active.append(tag_name)
            output.append(match.group(1))
        position = match.end()
    output.append(value[position:])
    for tag_name in reversed(active):
        output.append(f"</{tag_name}>")
    normalized = "".join(output)
    for _ in range(3):
        normalized = re.sub(r"<(latin|title|emphasis)>(\s+)", r"\2<\1>", normalized)
        normalized = re.sub(r"(\s+)</(latin|title|emphasis)>", r"</\2>\1", normalized)
    normalized = re.sub(r"([āēīōūĀĒĪŌŪ])<latin>", r"<latin>\1", normalized)
    normalized = re.sub(r"</latin>([āēīōūĀĒĪŌŪ])", r"\1</latin>", normalized)
    return normalized


def answer_spans(text: str) -> list[tuple[int, int]]:
    tokens = list(TOKEN_RE.finditer(text))
    spans: list[tuple[int, int]] = []
    excluded = {"AD", "BC", "A.D.", "B.C."}
    index = 0
    while index < len(tokens):
        token = tokens[index].group()
        letters = "".join(character for character in token if character.isalpha())
        previous_text = TAG_RE.sub("", text[:tokens[index].start()]).rstrip()
        follows_sentence_boundary = not previous_text or previous_text[-1] in "?.!"
        next_is_uppercase = (
            index + 1 < len(tokens) and is_upper_answer_token(tokens[index + 1].group())
        )
        single_letter_pronoun = letters == "I" and len(letters) == 1 and not next_is_uppercase
        candidate = (
            is_upper_answer_token(token)
            and letters not in excluded
            and not single_letter_pronoun
            and follows_sentence_boundary
        )
        if not candidate:
            index += 1
            continue

        end_index = index + 1
        parenthetical = token.startswith("(") and ")" not in token
        while end_index < len(tokens):
            next_token = tokens[end_index].group()
            if parenthetical:
                parenthetical = ")" not in next_token
                end_index += 1
                continue
            if is_upper_answer_token(next_token) or next_token.startswith("("):
                parenthetical = next_token.startswith("(") and ")" not in next_token
                end_index += 1
                continue
            break
        spans.append((tokens[index].start(), tokens[end_index - 1].end()))
        index = end_index
    return spans


def parse_pairs(block: str) -> list[tuple[str, str]]:
    spans = answer_spans(block)
    if not spans:
        return [(normalize_tags(block.strip()), "")]
    pairs: list[tuple[str, str]] = []
    question_start = 0
    for index, (answer_start, answer_end) in enumerate(spans):
        question = block[question_start:answer_start].strip(" .")
        question = re.sub(r"^\s*(?:TOSS[- ]?UP\s*)?\d+[.):]\s*", "", question, flags=re.IGNORECASE)
        answer = block[answer_start:answer_end].strip()
        if question:
            pairs.append((normalize_tags(question), normalize_tags(answer)))
        question_start = answer_end
    marker = re.search(r"see below for answers", block, re.IGNORECASE)
    if marker and len(pairs) == 1:
        answer = pairs[0][1]
        question = re.sub(
            r"^\s*(?:TOSS[- ]?UP\s*)?\d+[.):]\s*",
            "",
            block[:marker.start()].strip(" ."),
            flags=re.IGNORECASE,
        )
        follow_ups = re.findall(r"For five points, name two more\.", block[marker.end():], re.IGNORECASE)
        if follow_ups:
            return [(normalize_tags(question), block[marker.start():marker.end()])] + [
                (follow_up, answer) for follow_up in follow_ups
            ]
    if len(pairs) == 1:
        answer = pairs[0][1]
        trailing = block[spans[-1][1]:]
        follow_ups = re.findall(r"(?:Give|Name) (?:another|a third)\.", trailing, re.IGNORECASE)
        if follow_ups:
            return pairs + [(follow_up, answer) for follow_up in follow_ups]
    trailing = block[spans[-1][1]:].strip()
    if trailing and re.match(
        r"^(?:For\s+\w+\s+points?(?:\s+each)?,\s*)?"
        r"(?:what|who|when|where|why|how|name|give|translate|identify|which)\b",
        trailing,
        re.IGNORECASE,
    ):
        pairs.append((normalize_tags(trailing), ""))
    return pairs


def quoted(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_yaml(tournament: str, year: int, division: str, round_name: str, blocks: list[str]) -> str:
    lines = [
        f"tournament: {quoted(tournament)}",
        f"year: {year}",
        f"division: {quoted(division)}",
        f"round: {quoted(round_name)}",
        "questions:",
    ]
    for block in blocks:
        pairs = parse_pairs(block)
        tossup_question, tossup_answer = pairs[0]
        lines.extend(
            [
                "  - tossup:",
                f"      question: {quoted(tossup_question)}",
                f"      answer: {quoted(tossup_answer)}",
                "    boni:",
            ]
        )
        for bonus_question, bonus_answer in pairs[1:]:
            lines.extend(
                [
                    f"      - question: {quoted(bonus_question)}",
                    f"        answer: {quoted(bonus_answer)}",
                ]
            )
    return "\n".join(lines) + "\n"


def validate_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("questions"), list):
        raise ValueError(f"{path} does not contain the expected top-level schema")
    required = {"tournament", "year", "division", "round", "questions"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"{path} is missing: {', '.join(sorted(missing))}")
    for index, item in enumerate(data["questions"], 1):
        if not isinstance(item, dict) or not isinstance(item.get("tossup"), dict):
            raise ValueError(f"{path}: question {index} has no tossup")
        if not item.get("boni"):
            raise ValueError(f"{path}: question {index} has no bonuses")
    return data


def update_index() -> None:
    subprocess.run([sys.executable, "scripts/generate_index.py"], check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="RTF or plain-text source document")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for generated YAML files")
    parser.add_argument("--tournament", required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--division", required=True)
    parser.add_argument("--prefix", required=True, help="Filename prefix, e.g. njcl1997adv")
    parser.add_argument("--update-index", action="store_true", help="Regenerate questions/index.yaml afterward")
    parser.add_argument("--force", action="store_true", help="Overwrite existing YAML files")
    args = parser.parse_args()

    sections = split_sections(read_source(args.source))
    if not sections:
        raise SystemExit("No round headings found in source")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for label, lines in sections:
        round_name = display_round(label)
        blocks = question_blocks(lines)
        if not blocks:
            raise SystemExit(f"No numbered questions found under {label!r}")
        suffix = {
            "Round 1": "1",
            "Round 2": "2",
            "Round 3": "3",
            "Semifinals": "Semis",
            "Finals": "Finals",
            "Extra Questions": "Extras",
        }.get(round_name, re.sub(r"[^A-Za-z0-9]+", "", round_name))
        destination = args.output_dir / f"{args.prefix}{suffix}.yaml"
        if destination.exists() and not args.force:
            raise SystemExit(f"Refusing to overwrite {destination}; use --force")
        destination.write_text(
            render_yaml(args.tournament, args.year, args.division, round_name, blocks),
            encoding="utf-8",
        )
        data = validate_yaml(destination)
        print(f"{destination}: {data['round']} ({len(data['questions'])} draft questions)")

    if args.update_index:
        update_index()
        print("Updated questions/index.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())