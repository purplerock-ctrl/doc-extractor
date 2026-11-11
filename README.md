# Receipt Extractor

Upload a receipt or invoice (PDF or photo) and get clean, structured data back: vendor, date, subtotal, tax, total and currency. Results that look doubtful are flagged for human review.

**[Live demo](PASTE-YOUR-APP-LINK-HERE)** (password protected to control API costs)

![Screenshot of the app](screenshot.png)

## How it works

1. The document is sent to Claude (`claude-sonnet-5-5`) along with a strict schema that describes each field and the rules for filling it in.
2. The model's answer is validated with Pydantic, so malformed output is caught instead of saved.
3. Rule checks (for example, subtotal + tax must equal total) flag doubtful results for a person to review.
4. A batch pipeline processes whole folders of receipts in parallel and stores every result in SQLite, tagged with the prompt version and model, so experiments can be compared side by side.

## Results

Measured against hand-checked answer keys.

| Set | Receipts | All fields correct |
| --- | --- | --- |
| Training (instructions tuned on these) | 60 | 60/60 |
| Held back (never seen while tuning) | 10 | 10/10 |

- Model: `claude-sonnet-5-5`
- Average cost per receipt: about $0.006 (calculated from measured token usage × list prices)
- Average time per receipt: about 1.75 seconds
- Review flags: FLAGGED-COUNT of 60 receipts flagged, 0 errors missed

The full history of every experiment, including cheaper and stronger models, is in [results/experiments.md](results/experiments.md).

## What I learned

- **Check the answer key before changing the prompt.** Several apparent model errors turned out to be mistakes in my own labels.
- **Explicit rules beat clever prompting.** Writing each judgment call (tips, split payments, tax-included receipts, currency from the address) into the field descriptions took the first test set from 50% of receipts fully correct to 100%.
- **Held-back data is the honest test.** The training score shows how well the instructions fit; the held-back score shows whether they generalise.
- **Model updates can break working code.** A newer model rejected the way the original code forced tool use. Re-running the pipeline caught it immediately.
- **Detect what you can't prevent.** Rule checks would have flagged every reading error seen during development, so a person can review those instead of trusting them blindly.

## Limitations

- The test receipts are generated, so even the messy ones are tidier than real receipts. Expect lower accuracy on real-world documents.
- Ten held-back receipts is a small test set; one error would move the score by 10 points.
- Uploads are sent to Anthropic's API for processing and are not stored by this app.

## Project structure

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit web app: upload, review, save |
| `extract.py` | Sends a document to the model and returns a validated `Receipt` |
| `schema.py` | The `Receipt` fields and the rules for each |
| `checks.py` | Rule checks that flag doubtful results |
| `run_batch.py` | Processes a folder of receipts in parallel into SQLite |
| `score.py` | Compares results with the answer key and logs the scores |
| `LABELING.md` | The rules for what counts as the correct answer |

## Run it yourself

```
pip install -r requirements.txt
```

Create `.streamlit/secrets.toml` containing `ANTHROPIC_API_KEY` and `APP_PASSWORD`, then:

```
streamlit run app.py
```
