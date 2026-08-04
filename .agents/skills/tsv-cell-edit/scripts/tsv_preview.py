#!/usr/bin/env python3
"""
tsv_preview.py - Inspect a TSV file without counting tab characters.

Every row is printed as a JSON object keyed by column name, so nothing needs
to be counted or aligned by eye. Row numbers are 1-indexed and refer to DATA
rows only (row 1 = the first row after the header; the header is never row 1).

Usage:
  python tsv_preview.py file.tsv                 # summary: columns, row count, first/last row
  python tsv_preview.py file.tsv --row 5          # show data row 5 as a JSON object
  python tsv_preview.py file.tsv --rows 5-12      # show a range of data rows
  python tsv_preview.py file.tsv --grep "text"    # show every row containing "text" in any field
  python tsv_preview.py file.tsv --col status     # show one column's value for every row
"""
import csv
import json
import argparse


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        rows = list(reader)
    if not rows:
        raise SystemExit("Input file is empty")
    header, data = rows[0], [list(r) for r in rows[1:]]
    return header, data


def row_to_obj(header, row):
    obj = {}
    for i, colname in enumerate(header):
        obj[colname] = row[i] if i < len(row) else ""
    if len(row) != len(header):
        obj["_WARNING"] = f"row has {len(row)} fields but header has {len(header)}"
    return obj


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--row", type=int, help="show a single data row (1-indexed)")
    ap.add_argument("--rows", help="show a range of data rows, e.g. 5-12")
    ap.add_argument("--grep", help="show rows where any field contains this text (case-insensitive)")
    ap.add_argument("--col", help="show this column's value across all rows")
    args = ap.parse_args()

    header, data = load(args.file)

    if args.row is not None:
        idx = args.row - 1
        if not (0 <= idx < len(data)):
            raise SystemExit(f"Row {args.row} out of range (file has {len(data)} data rows)")
        print(json.dumps({"row": args.row, **row_to_obj(header, data[idx])}, ensure_ascii=False, indent=2))
        return

    if args.rows:
        start_s, end_s = args.rows.split("-")
        start, end = int(start_s), int(end_s)
        for i in range(start, end + 1):
            idx = i - 1
            if 0 <= idx < len(data):
                print(json.dumps({"row": i, **row_to_obj(header, data[idx])}, ensure_ascii=False))
        return

    if args.grep is not None:
        needle = args.grep.lower()
        found = False
        for i, row in enumerate(data, start=1):
            if any(needle in cell.lower() for cell in row):
                print(json.dumps({"row": i, **row_to_obj(header, row)}, ensure_ascii=False))
                found = True
        if not found:
            print(f"(no rows matched {args.grep!r})")
        return

    if args.col:
        if args.col not in header:
            raise SystemExit(f"Column {args.col!r} not found. Header columns: {header}")
        ci = header.index(args.col)
        for i, row in enumerate(data, start=1):
            val = row[ci] if ci < len(row) else ""
            print(json.dumps({"row": i, args.col: val}, ensure_ascii=False))
        return

    # default: summary
    print(
        json.dumps(
            {
                "columns": header,
                "num_columns": len(header),
                "num_data_rows": len(data),
                "first_row": row_to_obj(header, data[0]) if data else None,
                "last_row": row_to_obj(header, data[-1]) if data else None,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
