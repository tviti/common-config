---
name: tsv-cell-edit
description: Use this skill any time you need to edit, update, insert into, or append rows/columns to a TSV (tab-separated) file, especially files where many rows have empty/null columns. Trigger this whenever a .tsv file is mentioned, whenever the user asks to "edit this spreadsheet", "update a row", "insert a value into column X", "add a row", "fill in this cell", or similar, even if they don't say "TSV" explicitly and even if the file was only described as tab-delimited. Also use this whenever you are about to hand-edit tab-separated text yourself (via sed, direct string replacement, or writing out a row by hand) -- that approach is unreliable because tab characters are invisible and easy to miscount, especially in rows with several empty/null columns in a row. This skill replaces manual tab-editing with structured, validated, name-addressed edits.
---

# TSV Cell Edit

## The problem this solves

Tab characters are invisible. A row with several empty columns in a row
(`val1\t\t\t\tval2`) is very easy to miscount when reading or generating
tab-separated text directly -- this is true for LLMs in general and
especially for smaller/local models. Off-by-one tab errors silently shift
every value after the mistake into the wrong column.

The fix: **never read or write raw tab-delimited text directly.** Instead:
- *Read* rows through `tsv_preview.py`, which prints each row as a JSON
  object keyed by column name -- there's nothing to count.
- *Write* changes through `tsv_edit.py`, which takes edits as a list of
  `{row, col, value}`-style operations addressed by column **name**, applies
  them with Python's `csv` module (which is delimiter-exact by
  construction), and validates that every row still has the correct number
  of fields before anything is written to disk.

You (Claude) should never construct a tab-separated row by typing tab
characters yourself, and never use `sed`/`awk`/manual string splicing on a
TSV file. Always go through these two scripts.

## Workflow

### 1. Inspect the file

```bash
python3 scripts/tsv_preview.py file.tsv                 # header + row count + first/last row
python3 scripts/tsv_preview.py file.tsv --row 5          # data row 5 as {column: value}
python3 scripts/tsv_preview.py file.tsv --rows 5-12      # a range of rows
python3 scripts/tsv_preview.py file.tsv --grep "text"    # rows containing "text" in any field
python3 scripts/tsv_preview.py file.tsv --col status     # one column's value across all rows
```

Row numbers are **1-indexed and refer to data rows only** -- row 1 is the
first row after the header. Use this to find the exact row/column names you
need before editing; never eyeball the raw file to count tabs.

### 2. Write the edits as JSON, not as TSV text

Create an edits file (e.g. `edits.json`) describing what should change, as a
list of operations. Never write out a full replacement row as tab-separated
text -- use `set`/`set_row` and name only the columns that are actually
changing:

```json
{
  "operations": [
    {"op": "set",        "row": 5, "col": "status", "value": "done"},
    {"op": "set_row",    "row": 12, "values": {"notes": "checked", "priority": "high"}},
    {"op": "append_row", "values": {"id": "101", "status": "new"}},
    {"op": "insert_row", "row": 5, "values": {"id": "999"}},
    {"op": "add_column", "name": "flag", "default": ""}
  ]
}
```

Operation types:
| op | required fields | effect |
|---|---|---|
| `set` | `row`, `col`, `value` | set a single cell |
| `set_row` | `row`, `values` (dict) | set multiple cells in one row at once |
| `append_row` | `values` (dict) | add a new row at the end; unmentioned columns default to `""` |
| `insert_row` | `row`, `values` (dict) | insert a new row before position `row`; unmentioned columns default to `""` |
| `add_column` | `name`, optional `default` | add a new column to every row |

Rules:
- `col` and the keys inside `values` must match a header column name
  **exactly** (case-sensitive). An unknown column aborts the whole batch
  with the list of valid column names -- it never silently creates a new
  column via `set`/`set_row`.
- Any column not mentioned in `values` is left untouched (`set_row`) or
  defaulted to `""` (`append_row`/`insert_row`). This is exactly what makes
  mostly-null rows easy: you only ever specify the columns you actually care
  about, nothing else.
- All operations in the batch are validated before any are applied. If one
  op is invalid, nothing is written -- there's no partial/corrupted output.

### 3. Apply the edits

```bash
python3 scripts/tsv_edit.py input.tsv edits.json output.tsv
```

This prints a human-readable diff log (`set row 5, col 'status': '' ->
'done'`) and writes `output.tsv` only if every row validates against the
header's field count. Read the log back to the user (or check it yourself)
to confirm the changes match intent before treating the task as done.

By default it refuses to overwrite `input.tsv` in place -- pass a different
output path, or add `--force` if the user explicitly wants an in-place edit.

### 4. Verify

Re-run `tsv_preview.py` on the output file (or the specific rows you
changed) to confirm the edit landed correctly, and show that to the user.

## When *not* to use this skill

- **Bulk transforms across every row** (e.g. "uppercase the status column
  everywhere", "recompute a derived column for all 10,000 rows") are better
  done with a real columnar tool if one is available in the environment --
  `mlr` (Miller), `csvkit`, or `xsv`/`qsv` all handle whole-column
  operations more naturally than a row-by-row edit list. This skill is for
  targeted, LLM-driven inserts/updates, not mass reformatting.
- **Files where a field legitimately contains an embedded tab or newline**
  (rare in TSV, more common if the file was exported from something that
  didn't sanitize its data). Plain TSV has no standard escaping for this;
  if `tsv_edit.py` raises an error while writing, flag it to the user rather
  than trying to work around it with quoting guesses.

## Notes

- Both scripts are pure Python 3 standard library (`csv`, `json`,
  `argparse`) -- no extra dependencies required.
- Column/row references are always by name or 1-indexed data-row number,
  never by raw character/byte position, so nothing about the edit depends
  on correctly counting delimiters.
