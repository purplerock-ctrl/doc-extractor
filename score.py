import csv
import sqlite3

from db import connect
from normalize import norm_text, norm_money, norm_date

PROMPT_VERSION = "v1"
RULES = {"vendor": norm_text, "date": norm_date, "subtotal": norm_money,
         "tax": norm_money, "total": norm_money, "currency": norm_text}

conn = connect()
conn.row_factory = sqlite3.Row      # lets you read columns by name

with open("data/labels.csv", newline="") as f:
    labels = list(csv.DictReader(f))

correct = {field: 0 for field in RULES}
all_right = 0
failures = []

for label in labels:
    row = conn.execute(
        "SELECT * FROM extractions WHERE doc_id=? AND prompt_version=?",
        (label["doc_id"], PROMPT_VERSION)).fetchone()
    doc_ok = True
    for field, clean in RULES.items():
        expected = clean(label[field])
        got = clean(row[field]) if row else None
        if expected == got:
            correct[field] += 1
        else:
            doc_ok = False
            failures.append([label["doc_id"], field, expected, got])
    if doc_ok:
        all_right += 1

n = len(labels)
for field in RULES:
    print(f"{field:10} {correct[field]}/{n} = {correct[field] / n:.0%}")
print(f"all fields right: {all_right}/{n} = {all_right / n:.0%}")

with open("failures.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["doc_id", "field", "expected", "got"])
    writer.writerows(failures)