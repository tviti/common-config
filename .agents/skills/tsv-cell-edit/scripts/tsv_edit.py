#!/usr/bin/env python3
"""
tsv_edit.py - Apply structured edits to a TSV file without hand-editing
tab-delimited text.

Usage:
  python tsv_edit.py input.tsv edits.json output.tsv [--force]

edits.json format:
{
  "operations": [
    {"op": "set",        "row": 5, "col": "status", "value": "done"},
    {"op": "set_row",    "row": 5, "values": {"status": "done", "notes": "checked"}},
    {"op": "append_row", "values": {"id": "101", "status": "new"}},
    {"op": "insert_row", "row": 5, "values": {"id": "999"}},
    {"op": "add_column", "name": "flag", "default": ""}
  ]
}

Rules:
- "row" is 1-indexed and refers to DATA rows (row 1 = the first row after
  the header). The header itself is never row 1.
- "col" / the keys inside "values" must match header column names exactly
  (case-sensitive). Referencing an unknown column aborts with the list of
  valid names -- columns are never silently created by "set"/"set_row".
- For "set_row" and "insert_row"/"append_row", any column not mentioned in
  "values" is left as-is (set_row) or defaulted to "" (append_row/insert_row
  on a brand new row). This is the safe way to handle rows that are mostly
  null columns: you only ever specify the columns you actually care about.
- Every operation is validated against the header before anything is
  written. If ANY operation is invalid, the script aborts and writes
  nothing -- it never partially applies a batch of edits.
- After applying all edits, every row is checked to have exactly the same
  number of fields as the header. If that check fails, nothing is written.
"""
import argparse
import copy
import csv
import json


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        rows = list(reader)
    if not rows:
        raise SystemExit("Input file is empty")
    header, data = rows[0], [list(r) for r in rows[1:]]
    return header, data


def ensure_col(header, name):
    if name not in header:
        raise SystemExit(f"Unknown column {name!r}. Valid columns: {header}")
    return header.index(name)


def values_to_row(header, values, default=""):
    row = [default] * len(header)
    for k, v in values.items():
        ci = ensure_col(header, k)
        row[ci] = v
    return row


def apply(header, data, operations):
    header = list(header)
    data = copy.deepcopy(data)
    log = []

    for n, op in enumerate(operations, start=1):
        kind = op.get("op")

        if kind == "set":
            row_i, col, val = op["row"], op["col"], op["value"]
            ci = ensure_col(header, col)
            if not (1 <= row_i <= len(data)):
                raise SystemExit(f"Op {n}: row {row_i} out of range (1-{len(data)})")
            r = data[row_i - 1]
            while len(r) < len(header):
                r.append("")
            old = r[ci]
            r[ci] = val
            log.append(f"set row {row_i}, col {col!r}: {old!r} -> {val!r}")

        elif kind == "set_row":
            row_i, values = op["row"], op["values"]
            if not (1 <= row_i <= len(data)):
                raise SystemExit(f"Op {n}: row {row_i} out of range (1-{len(data)})")
            r = data[row_i - 1]
            while len(r) < len(header):
                r.append("")
            for k, v in values.items():
                ci = ensure_col(header, k)
                old = r[ci]
                r[ci] = v
                log.append(f"set row {row_i}, col {k!r}: {old!r} -> {v!r}")

        elif kind == "append_row":
            new_row = values_to_row(header, op["values"])
            data.append(new_row)
            log.append(f"appended row {len(data)}: {op['values']}")

        elif kind == "insert_row":
            row_i, values = op["row"], op["values"]
            new_row = values_to_row(header, values)
            insert_at = row_i - 1
            if not (0 <= insert_at <= len(data)):
                raise SystemExit(f"Op {n}: insert row {row_i} out of range")
            data.insert(insert_at, new_row)
            log.append(f"inserted new row at position {row_i}: {values}")

        elif kind == "add_column":
            name, default = op["name"], op.get("default", "")
            if name in header:
                raise SystemExit(f"Op {n}: column {name!r} already exists")
            header.append(name)
            for r in data:
                r.append(default)
            log.append(f"added column {name!r} with default {default!r}")

        else:
            raise SystemExit(f"Op {n}: unknown op {kind!r}")

    # Final validation: every row must match the header length exactly.
    for i, r in enumerate(data, start=1):
        if len(r) != len(header):
            raise SystemExit(
                f"VALIDATION FAILED: row {i} has {len(r)} fields, header has "
                f"{len(header)}. No output written."
            )

    return header, data, log


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("edits_json")
    ap.add_argument("output")
    ap.add_argument("--force", action="store_true", help="allow output to overwrite input")
    args = ap.parse_args()

    if args.output == args.input and not args.force:
        raise SystemExit("Refusing to overwrite the input file without --force")

    header, data = load(args.input)
    with open(args.edits_json, encoding="utf-8") as f:
        spec = json.load(f)

    new_header, new_data, log = apply(header, data, spec["operations"])

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONE, lineterminator="\n")
        writer.writerow(new_header)
        writer.writerows(new_data)

    print(f"Applied {len(spec['operations'])} operation(s):")
    for line in log:
        print(f"  - {line}")
    print(f"Wrote {len(new_data)} data rows, {len(new_header)} columns to {args.output}")


if __name__ == "__main__":
    main()
