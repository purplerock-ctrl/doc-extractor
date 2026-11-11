import sqlite3
import sys

version = sys.argv[1]
model = sys.argv[2]

conn = sqlite3.connect("receipts.db")
rows = conn.execute(
    "SELECT doc_id, review_reasons FROM extractions "
    "WHERE prompt_version=? AND model=? AND needs_review=1 "
    "ORDER BY doc_id",
    (version, model)).fetchall()

total = conn.execute(
    "SELECT COUNT(*) FROM extractions WHERE prompt_version=? AND model=?",
    (version, model)).fetchone()[0]

for doc_id, reasons in rows:
    print(f"{doc_id:10} {reasons}")
print(f"\n{len(rows)} of {total} receipts flagged for review")