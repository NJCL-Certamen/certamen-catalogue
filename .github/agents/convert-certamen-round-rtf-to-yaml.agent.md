---
name: convert-certamen-round-rtf-to-yaml
description: "Use this agent when converting a Certamen round document from RTF or plain text into YAML files for the Certamen Question Catalogue Project. It handles round splitting, question extraction, formatting-tag preservation, and validation against the repository schema."
---

# Convert Certamen Round RTF to YAML

You are helping convert a source round document into the repository’s YAML format for Certamen questions.

## Goal

Turn a round source file such as an RTF or text dump into one or more YAML files in the project’s expected directory and schema, preserving tournament metadata, division, round name, and pseudo-formatting tags.

## Repository conventions

- Use the project’s standard YAML schema from the existing question files.
- Keep all question and answer fields quoted in double quotes.
- Preserve formatting tags when present:
  - `<latin>...</latin>`
  - `<title>...</title>`
  - `<emphasis>...</emphasis>`
- Do not invent other HTML-like tags.
- Prefer wrapping a whole phrase in a single pseudo-tag rather than tagging each word separately.
- For each question, keep the structure:

```yaml
tournament: <Tournament>
year: <Year>
division: <Division>
round: <Round>
questions:
  - tossup:
      question: "<question>"
      answer: "<answer>"
    boni:
      - question: "<bonus 1 question>"
        answer: "<bonus 1 answer>"
      - question: "<bonus 2 question>"
        answer: "<bonus 2 answer>"
```

## Workflow

### 1. Locate and inspect the source

- Identify the input file and confirm whether it is RTF, plain text, or a mixed-encoding dump.
- Check whether the document includes a tournament header, year, division, and round headings.
- If the source is RTF, use `scripts/convert_certamen_round.py` so the decoder retains formatting state. Do not use a plain-text-only RTF conversion for final output because it loses `\\b`, `\\i`, and `\\ul` boundaries.

### 2. Determine the target output structure

- Decide the target directory based on tournament and year.
- Common pattern:
  - `questions/njcl/<year>/<division>/`
- Determine the number of rounds in the document and whether there are extra questions or finals/semi-finals sections.
- Create output files per round, not one monolithic file, unless the source clearly represents a single round.

### 3. Split by round

- Scan the plain-text output for round markers such as:
  - `ROUND ONE`
  - `ROUND TWO`
  - `ROUND THREE`
  - `SEMI-FINAL`
  - `FINAL ROUND`
  - `EXTRA QUESTIONS`
- Confirm the section boundaries before extracting questions.
- Keep each round in a separate YAML file with a project-style file name.

### 4. Extract questions and answers

For each round:

- Identify tossup entries by their number and question/answer pattern.
- Identify bonus entries as `B1`, `B2`, etc., or similar patterns.
- Capture:
  - tossup question
  - tossup answer
  - each bonus question
  - each bonus answer
- Preserve punctuation and RTF formatting with these exact mappings:
  - bold (`\\b`): `<latin>...</latin>`
  - italic (`\\i`): `<title>...</title>`
  - underline (`\\ul`): `<emphasis>...</emphasis>`
- Keep nested tags when multiple styles are active, and balance tags after splitting question and answer fields.
- If an answer is abbreviated or includes alternate acceptable forms, preserve the exact source text in the YAML value.

### 5. Convert to YAML

Write the output in the project’s standard YAML format with all question and answer strings quoted.

Important validation rules:

- All question and answer fields must be string values wrapped in double quotes.
- Pseudo-tags must appear only as `<latin>`, `<title>`, and `<emphasis>`.
- Do not use Markdown code fences inside the produced YAML.
- Ensure the file is valid YAML and parseable by the repo’s Python tooling.

### 6. Validate and repair

After writing the YAML files:

- Parse each YAML file using `yaml.safe_load`.
- Verify the file has the expected structure:
  - `tournament`
  - `year`
  - `division`
  - `round`
  - `questions`
- Confirm each question entry contains a tossup and at least one bonus.
- Check that the round count matches the source document.
- Check that all required pseudo-tags are present where the source needed them.

### 7. Update the catalog

- Add the new round entries to `questions/index.yaml` using the repo’s established format.
- Ensure the relative paths and labels match the generated YAML files.

## Useful project examples

Consult these existing files while converting:

- `questions/njcl/1979/upper/njcl1979adv1.yaml`
- `questions/njcl/1997/upper/*.yaml` when available
- `questions/index.yaml`
- `.github/skills/convert-certamen-round-to-yaml/SKILL.md`

## One-time implementation pattern

For a repeatable draft conversion, use the repository helper:

```bash
python scripts/convert_certamen_round.py SOURCE.rtf \
  --output-dir questions/njcl/YEAR/DIVISION \
  --tournament "NJCL Certamen" \
  --year YEAR \
  --division Division \
  --prefix njclYEARprefix
```

The helper merges repeated page-header headings, preserves RTF formatting, writes one file per detected section, validates each generated YAML file, and refuses to overwrite existing files unless `--force` is supplied. It must not invent `SEE BELOW`; retain that text only when it appears literally in the source.

Use a Python script to inspect the source before conversion when the file is in RTF form:

```python
from pathlib import Path
import re

p = Path('temp/97njcl_upp.rtf')
text = p.read_text(encoding='latin-1', errors='ignore')
print(text[:2000])
```

Then inspect round headings and split by section before writing YAML.

## Quality bar before finishing

A conversion is complete only when all of the following are true:

- the output files are in the right directory,
- the YAML parses successfully,
- the round counts are correct,
- the pseudo-formatting tags are preserved,
- every `<latin>`, `<title>`, and `<emphasis>` tag is balanced,
- bold, italic, and underlined source spans map to the required pseudo-tags,
- long vowels (ā, ē, ī, ō, ū) that are adjacent to `<latin>` tags are moved inside the latin tags,
- spaces at the start or end of a tagged section is moved outside of the tag,
- no synthetic `SEE BELOW` value was introduced,
- `questions/index.yaml` has been updated,
- the source document has been split into the right round files rather than left as one blob.

## Failure patterns to watch for

- Unescaped quotes inside question strings.
- Correct sections but wrong metadata such as tournament name or division.
- Merged rounds that should be separate files.
- Missing formatting tags for Latin text, titles, or emphasized phrases.
- YAML parsing errors caused by unquoted colons or malformed nested lists.

## Final instruction

Do the conversion in a way that is reproducible, reviewable, and project-conformant. If the source format is messy, fix the extraction logic first and verify the round boundaries before writing final YAML.
