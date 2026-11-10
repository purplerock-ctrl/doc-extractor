import base64
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from pydantic import ValidationError

from schema import Receipt

load_dotenv()
client = anthropic.Anthropic()
MODEL = "claude-haiku-5-5"  # copy a current model name from the docs

MEDIA_TYPES = {".pdf": "application/pdf", ".jpg": "image/jpeg",
               ".jpeg": "image/jpeg", ".png": "image/png"}

def extract(path):
    path = Path(path)
    media_type = MEDIA_TYPES[path.suffix.lower()]
    data = base64.standard_b64encode(path.read_bytes()).decode("utf-8")

    block_type = "document" if media_type == "application/pdf" else "image"
    file_block = {"type": block_type,
                  "source": {"type": "base64", "media_type": media_type, "data": data}}

    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        tools=[{"name": "save_receipt",
                "description": "Save the fields read from the receipt.",
                "input_schema": Receipt.model_json_schema()}],
        tool_choice={"type": "tool", "name": "save_receipt"},
        messages=[{"role": "user", "content": [
            file_block,
            {"type": "text", "text": "Extract the receipt fields. "
                                     "Use null for anything not shown. Never guess."},
        ]}],
    )

    for block in response.content:
        if block.type == "tool_use":
            return Receipt.model_validate(block.input)
    raise ValueError("The model did not return receipt fields")

if __name__ == "__main__":
    try:
        print(extract(sys.argv[1]))
    except ValidationError as error:
        print("Output did not match the schema:", error)