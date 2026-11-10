import time
from pathlib import Path

import anthropic

from db import connect
from extract import extract, MODEL, MEDIA_TYPES

PROMPT_VERSION = "v1"
conn = connect()

def already_done(doc_id):
    row = conn.execute(
        "SELECT 1 FROM extractions WHERE doc_id=? AND prompt_version=? AND model=?",
        (doc_id, PROMPT_VERSION, MODEL)).fetchone()
    return row is not None

def extract_with_retry(path):
    for wait in [2, 4, 8]:
        try:
            return extract(path)
        except (anthropic.RateLimitError, anthropic.InternalServerError):
            time.sleep(wait)
    return extract(path)  # final attempt; a failure here is logged below

for path in sorted(Path("data/raw").iterdir()):
    if path.suffix.lower() not in MEDIA_TYPES:
        continue                      # skip stray files such as .DS_Store
    doc_id = path.name
    if already_done(doc_id):
        continue                      # skip work already saved
    try:
        start = time.time()
        receipt, usage = extract_with_retry(path)
        seconds = time.time() - start
        conn.execute(
            "INSERT INTO extractions (doc_id, prompt_version, model, vendor, date, "
            "subtotal, tax, total, currency, input_tokens, output_tokens, seconds) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (doc_id, PROMPT_VERSION, MODEL, receipt.vendor, receipt.date,
             receipt.subtotal, receipt.tax, receipt.total, receipt.currency,
             usage.input_tokens, usage.output_tokens, seconds))
        conn.commit()
        print("ok", doc_id)
    except Exception as error:
        conn.execute("INSERT INTO errors (doc_id, message) VALUES (?, ?)",
                     (doc_id, str(error)))
        conn.commit()
        print("FAILED", doc_id, error)