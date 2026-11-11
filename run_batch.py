import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import anthropic

from db import connect
from extract import extract, MEDIA_TYPES

from checks import check


def already_done(conn, doc_id, version, model):
    row = conn.execute(
        "SELECT 1 FROM extractions WHERE doc_id=? AND prompt_version=? AND model=?",
        (doc_id, version, model)).fetchone()
    return row is not None


def extract_with_retry(path, model):
    for wait in [2, 4, 8]:
        try:
            return extract(path, model)
        except (anthropic.RateLimitError, anthropic.InternalServerError):
            time.sleep(wait)
    return extract(path, model)  # final attempt; a failure here is logged below


def timed_extract(path, model):
    """Runs in a worker thread: extract one receipt and time it."""
    start = time.time()
    receipt, usage = extract_with_retry(path, model)
    return receipt, usage, time.time() - start


def main():
    parser = argparse.ArgumentParser(description="Extract all receipts in a folder.")
    parser.add_argument("version", help="Prompt or extraction version label")
    parser.add_argument("model", help="Anthropic model name")
    parser.add_argument("--workers", type=int, default=5,
                        help="How many receipts to process at once (default 5)")
    parser.add_argument("--folder", default="data/raw",
                        help="Folder of receipts to process (default data/raw)")
    args = parser.parse_args()

    conn = connect()

    # Work out what still needs doing before starting
    todo = [p for p in sorted(Path(args.folder).iterdir())
            if p.suffix.lower() in MEDIA_TYPES          # skip stray files such as .DS_Store
            and not already_done(conn, p.name, args.version, args.model)]
    print(f"{len(todo)} receipts to process with {args.model} ({args.version}), "
          f"{args.workers} at a time")
    run_start = time.time()
    ok = failed = 0

    # Send several receipts at once; save each result as it finishes.
    # All database writes happen here in the main thread, which SQLite needs.
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        jobs = {pool.submit(timed_extract, p, args.model): p for p in todo}
        for job in as_completed(jobs):
            doc_id = jobs[job].name
            try:
                receipt, usage, seconds = job.result()
                problems = check(receipt)
                conn.execute(
                    "INSERT INTO extractions (doc_id, prompt_version, model, vendor, date, "
                    "subtotal, tax, total, currency, input_tokens, output_tokens, seconds, needs_review, review_reasons) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (doc_id, args.version, args.model, receipt.vendor, receipt.date,
                     receipt.subtotal, receipt.tax, receipt.total, receipt.currency,
                     usage.input_tokens, usage.output_tokens, seconds, 1 if problems else 0, "; ".join(problems)))
                conn.commit()
                ok += 1
                print("ok", doc_id, "(needs review: " + "; ".join(problems) + ")" if problems else "")
            except Exception as error:
                conn.execute("INSERT INTO errors (doc_id, message) VALUES (?, ?)",
                             (doc_id, str(error)))
                conn.commit()
                failed += 1
                print("FAILED", doc_id, error)

    print(f"Done: {ok} ok, {failed} failed, in {time.time() - run_start:.0f} seconds")


if __name__ == "__main__":
    main()