import re

def norm_text(value):
    if value is None or value == "":
        return None
    value = str(value).lower()
    value = re.sub(r"\b(inc|llc|ltd|co|corp)\b", "", value)   # drop company suffixes
    value = re.sub(r"[^a-z0-9 ]", "", value)                  # drop punctuation
    return " ".join(value.split())                            # tidy spaces

def norm_money(value):
    if value is None or value == "":
        return None
    return round(float(str(value).replace("$", "").replace(",", "")), 2)

def norm_date(value):
    if value is None or value == "":
        return None
    return str(value).strip()