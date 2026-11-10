---
name: touch-up-certamen-round-yaml
description: "Use when cleaning up, proofreading, repairing, or polishing an existing Certamen round YAML file, especially when removing placeholders, fixing misplaced questions or answers, preserving accepted answer variants, or completing the standard 20-question structure."
---

# Touch Up Certamen Round YAML

You edit existing Certamen round YAML files into clean, complete, repository-style question files. This is a cleanup and proofreading workflow, not a source-document conversion. Preserve the author's content and make only supported corrections.

## Workflow

1. Read the entire target file and inspect the repository's conversion skill and a finished YAML file from the questions/ folder for the applicable schema and conventions.
2. Count the question entries and identify placeholders, missing fields, duplicated entries, and content that appears to be in the wrong field.
3. Repair structure without losing content:
   - A question entry has one `tossup` with `question` and `answer`, plus exactly two `boni`, each with `question` and `answer`, when the requested round uses the standard format.
   - Remove entries that are wholly empty placeholders, such as a tossup whose question and answer are both `"."`.
   - If only one field is `"."`, do not discard the entry. Check adjacent fields and available source material for a displaced prompt or answer. Restore it only when the intended pairing is clear; otherwise ask the user rather than guessing.
   - Watch for question text placed in an `answer` field, an answer appended to a question, or the next question embedded after an answer. Separate these only when the boundary and pairing are evident from context or source material.
   - Preserve question order and all meaningful answer alternatives. Do not silently drop valid variants.
4. Polish wording and presentation conservatively:
   - Quote every `question` and `answer` value in double quotes.
   - Keep prompts complete and clear. If a fragment can be expanded from nearby context without changing its meaning, make the wording consistent with the rest of the round.
   - Preserve initials, parenthetical forms, and other accepted answer variants when present or supported by the source. Use the repository's established separator style for alternatives.
   - Mark Latin text with `<latin>...</latin>`, literary titles with `<title>...</title>`, and other source emphasis with `<emphasis>...</emphasis>`. Use only these pseudo-tags, balance them, and avoid doubling a tag. Do not tag ordinary English merely because it discusses Latin.
   - Preserve the file's Latin spelling and diacritics unless the source or a reliable local reference supports a correction. Do not add or remove macrons, diacritics, or alternate answers based only on guesswork.
5. Validate the finished file:
   - Parse it as YAML using the repository's available Python YAML tooling when feasible.
   - Confirm there are no `"."` placeholders left in question or answer fields.
   - Confirm every entry has the required fields and exactly two complete bonuses when that is the requested format.
   - If the user specifies 20 questions, verify there are exactly 20. Do not pad a shorter source round or discard meaningful entries just to reach 20.
   - Check for unquoted values, malformed pseudo-tags, accidental content loss, and unrelated changes.

## Boundaries

- Never invent a missing question, answer, historical fact, alternate answer, or Latin form.
- Do not rewrite or “correct” content that is uncertain; preserve it and report the uncertainty or ask the user.
- Do not change tournament metadata, question order, or accepted answers without a clear reason.
- Do not modify the example file or unrelated rounds.
- Report the file changed, the structural result, any unresolved ambiguities, and the validation performed.
