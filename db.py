import sqlite3

def connect():
    conn = sqlite3.connect("receipts.db")
    conn.execute("""CREATE TABLE IF NOT EXISTS extractions (
        doc_id TEXT, prompt_version TEXT, model TEXT,
        vendor TEXT, date TEXT, subtotal REAL, tax REAL, total REAL, currency TEXT,
        input_tokens INTEGER, output_tokens INTEGER, seconds REAL,
        needs_review INTEGER, review_reasons TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (doc_id, prompt_version, model))""")
    conn.execute("""CREATE TABLE IF NOT EXISTS errors (
        doc_id TEXT, message TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    return conn