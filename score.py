import argparse
import csv
import sqlite3
from datetime import date
from pathlib import Path

from db import connect
from normalize import norm_text, norm_money, norm_date

RULES = {"vendor": norm_text, "date": norm_date, "subtotal": norm_money,
         "tax": norm_money, "total": norm_money, "currency": norm_text}
PRICES = {
    "claude-fable-5-2": {"input": 8.0, "output": 40.0},
    "claude-mythos-5-2": {"input": 8.0, "output": 40.0},
    "claude-fable-5-1": {"input": 10.0, "output": 50.0},
    "claude-mythos-5-1": {"input": 10.0, "output": 50.0},
    "claude-fable-5": {"input": 10.0, "output": 50.0},
    "claude-mythos-5": {"input": 10.0, "output": 50.0},
    "claude-opus-5-5": {"input": 4.0, "output": 20.0},
    "claude-opus-5": {"input": 5.0, "output": 25.0},
    "claude-opus-4-8": {"input": 5.0, "output": 25.0},
    "claude-opus-4-7": {"input": 5.0, "output": 25.0},
    "claude-opus-4-6": {"input": 5.0, "output": 25.0},
    "claude-opus-4-5": {"input": 5.0, "output": 25.0},
    "claude-sonnet-5-5": {"input": 2.0, "output": 10.0},
    "claude-sonnet-5": {"input": 2.0, "output": 10.0},
    "claude-sonnet-4-6": {"input": 3.0, "output": 15.0},
    "claude-sonnet-4-5": {"input": 3.0, "output": 15.0},
    "claude-sonnet-4": {"input": 3.0, "output": 15.0},
    "claude-haiku-5-5": {"input": 0.10, "output": 0.50},
    "claude-haiku-4-5": {"input": 1.0, "output": 5.0},
}


def prices_for(model, input_tokens):
    for model_id, prices in PRICES.items():
        if model == model_id or model.startswith(model_id + "-"):
            if model_id == "claude-haiku-5-5" and input_tokens > 100_000:
                return {"input": 0.50, "output": 2.50}
            return prices
    return None


def document_cost(model, input_tokens, output_tokens):
    prices = prices_for(model, input_tokens)
    if prices is None:
        return None
    return (input_tokens * prices["input"] + output_tokens * prices["output"]) / 1_000_000

def main():
    parser = argparse.ArgumentParser(description="Score receipt extractions.")
    parser.add_argument("version", help="Prompt or extraction version label")
    parser.add_argument("model", help="Anthropic model name")
    parser.add_argument("note", nargs="?", default="", help="Short description of this run")
    parser.add_argument("--labels", type=Path, default=Path("data/labels.csv"),
                        help="Path to the labels CSV (default: data/labels.csv)")
    args = parser.parse_args()
    VERSION = args.version
    MODEL = args.model

    conn = connect()
    conn.row_factory = sqlite3.Row      # lets you read columns by name

    with args.labels.open(newline="") as f:
        labels = list(csv.DictReader(f))

    correct = {field: 0 for field in RULES}
    all_right = 0
    failures = []
    usage_totals = {"input_tokens": 0, "output_tokens": 0, "seconds": 0.0}
    costs = []
    extraction_count = 0

    for label in labels:
        row = conn.execute(
            "SELECT * FROM extractions WHERE doc_id=? AND prompt_version=? AND model=?",
            (label["doc_id"], VERSION, MODEL)).fetchone()
        if row:
            input_tokens = row["input_tokens"] or 0
            output_tokens = row["output_tokens"] or 0
            usage_totals["input_tokens"] += input_tokens
            usage_totals["output_tokens"] += output_tokens
            usage_totals["seconds"] += row["seconds"] or 0.0
            extraction_count += 1
            costs.append(document_cost(MODEL, input_tokens, output_tokens))
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
    print(f"version: {VERSION}; model: {MODEL}")
    for field in RULES:
        score = f"{correct[field] / n:.0%}" if n else "N/A"
        print(f"{field:10} {correct[field]}/{n} = {score}")
    score = f"{all_right / n:.0%}" if n else "N/A"
    print(f"all fields right: {all_right}/{n} = {score}")

    if extraction_count:
        print(f"average input tokens per document: "
              f"{usage_totals['input_tokens'] / extraction_count:.1f}")
        print(f"average output tokens per document: "
              f"{usage_totals['output_tokens'] / extraction_count:.1f}")
        print(f"average seconds per document: "
              f"{usage_totals['seconds'] / extraction_count:.2f}")
        if all(cost is not None for cost in costs):
            print(f"average cost per document: "
                  f"${sum(costs) / extraction_count:.6f} USD")
        else:
            print(f"average cost per document: N/A (no configured Anthropic price "
                  f"for {MODEL})")
    else:
        print("average input tokens per document: N/A (no extractions)")
        print("average output tokens per document: N/A (no extractions)")
        print("average seconds per document: N/A (no extractions)")
        print("average cost per document: N/A (no extractions)")

    with open("failures.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["doc_id", "field", "expected", "got"])
        writer.writerows(failures)

    avg_in, avg_out, avg_sec = conn.execute(
        "SELECT AVG(input_tokens), AVG(output_tokens), AVG(seconds) "
        "FROM extractions WHERE prompt_version=? AND model=?",
        (VERSION, MODEL)).fetchone()
    if avg_in is not None:
        run_rows = conn.execute(
            "SELECT input_tokens, output_tokens FROM extractions "
            "WHERE prompt_version=? AND model=?",
            (VERSION, MODEL)).fetchall()
        run_costs = [document_cost(MODEL, row[0] or 0, row[1] or 0)
                     for row in run_rows]
        cost = sum(run_costs) / len(run_costs) if all(
            value is not None for value in run_costs) else None
    else:
        cost = None

    log = Path("results/experiments.md")
    log.parent.mkdir(parents=True, exist_ok=True)
    if not log.exists():
        fields = " | ".join(RULES)
        log.write_text(
            f"| Date | Run | Model | What changed | {fields} | All fields | "
            "Cost/doc (calc.) | Sec/doc |\n"
            "|" + " --- |" * (len(RULES) + 7) + "\n",
            encoding="utf-8")

    scores = " | ".join(f"{correct[field]}/{n}" for field in RULES)
    note = args.note.replace("|", "\\|").replace("\r", " ").replace("\n", " ")
    cost_text = f"${cost:.4f}" if cost is not None else "N/A"
    seconds_text = f"{avg_sec:.1f}" if avg_sec is not None else "N/A"
    log_row = (f"| {date.today()} | {VERSION} | {MODEL} | {note} | {scores} | "
               f"{all_right}/{n} | {cost_text} | {seconds_text} |\n")
    with log.open("a", encoding="utf-8") as f:
        f.write(log_row)
    print("Logged to", log)


if __name__ == "__main__":
    main()

