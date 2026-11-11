from datetime import date

def check(receipt):
    problems = []

    if receipt.vendor is None:
        problems.append("vendor missing")

    if receipt.total is None:
        problems.append("total missing")
    elif receipt.total <= 0:
        problems.append("total is not positive")

    if None not in (receipt.subtotal, receipt.tax, receipt.total):
        if abs(receipt.subtotal + receipt.tax - receipt.total) > 0.01:
            problems.append("subtotal + tax does not equal total")

    if receipt.date is not None:
        try:
            if date.fromisoformat(receipt.date) > date.today():
                problems.append("date is in the future")
        except ValueError:
            problems.append("date is not in YYYY-MM-DD form")

    return problems      # an empty list means nothing looked wrong