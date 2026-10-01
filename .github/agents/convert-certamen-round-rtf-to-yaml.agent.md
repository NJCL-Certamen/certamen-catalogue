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
- For NJCL material, keep the tournament namespace in the path: `questions/njcl/<year>/<division>/`. Do not drop the `njcl/` segment when the user gives a shorthand path. Keep the directory name and YAML `division` metadata consistent with nearby files; older NJCL `lower` folders may use `Intermediate` as the metadata value.
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
- Preserve punctuation and RTF formatting with these mappings:
  - bold (`\\b`): usually `<latin>...</latin>` for Latin text
  - italic (`\\i`): classify by meaning, not style alone: Latin text uses `<latin>`, actual literary work titles use `<title>`, and editorial notes or other emphasis use `<emphasis>`
  - underline (`\\ul`): `<emphasis>...</emphasis>`
- A styled span may mix semantic kinds of text; split it into appropriate tags instead of wrapping all italics as a title.
- Keep nested tags when multiple styles are active, and balance tags after splitting question and answer fields.
- Avoid nesting an emphasis tag inside another emphasis tag; flatten a continuous emphasized span so the repository tag checker can validate it.
- If an answer is abbreviated or includes alternate acceptable forms, preserve the exact source text in the YAML value.
- Check numeric answers and alternatives carefully. Numbers such as counts or dates can be answers, not part of the preceding question.
- If the source has a prompt with no keyed answer, do not guess. Preserve it using the schema’s accepted empty-answer representation and report the source gap.

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

### 7. Leave the generated index alone

- Do not edit, regenerate, or add entries to `questions/index.yaml` during conversion. It is generated by the GitHub workflow after changes are pushed.
- Do not run `scripts/generate_index.py` as part of a routine round conversion.
- Do not modify `scripts/convert_certamen_round.py` or other shared conversion scripts during a routine data conversion. If the helper has a source-specific bug, keep the YAML output correct without unrelated changes and report the tooling issue separately unless the user asks to change the tool.

## Useful project examples

Consult these existing files while converting:

- `questions/njcl/1979/upper/njcl1979adv1.yaml`
- `questions/njcl/1997/upper/*.yaml` when available
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

Do not use `--force` to overwrite existing round files unless the user explicitly asks. Do not regenerate the catalog index after conversion.

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
- every printed answer and accepted alternative is attached to the correct prompt, including numeric answers,
- genuinely unkeyed prompts have no invented answers and are called out in the final report,
- `questions/index.yaml` has not been modified,
- the source document has been split into the right round files rather than left as one blob.

## Failure patterns to watch for

- Unescaped quotes inside question strings.
- Correct sections but wrong metadata such as tournament name or division.
- Merged rounds that should be separate files.
- Missing formatting tags for Latin text, titles, or emphasized phrases.
- Italic text tagged as a literary title without checking its meaning.
- Numeric answers or alternate accepted forms attached to the wrong prompt or omitted.
- YAML parsing errors caused by unquoted colons or malformed nested lists.

## Final instruction

Do the conversion in a way that is reproducible, reviewable, and project-conformant. If the source format is messy, fix the extraction logic first and verify the round boundaries before writing final YAML.
