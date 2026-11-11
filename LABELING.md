# Labelling rules

How the correct answer is decided for each field. When a rule changes,
update labels.csv and the matching description in schema.py too.

## Vendor
- The business name printed at the top of the receipt.
- If a different legal name appears elsewhere (e.g. footer), still use the top name.

## Date
- The purchase or invoice date, as YYYY-MM-DD.
- Ignore due dates, pick-up/ready dates and print times.
- Two-digit years mean 20XX.
- Non-US numeric dates are day/month/year; use address and currency to decide.

## Subtotal
- Amount before tax, after discounts and coupons, as printed.
- Empty if no subtotal line is printed. Never calculated.
- Tax-included receipts (TTC, VAT included) with no subtotal line: empty.

## Tax
- The tax amount as printed. 0 if the tax line shows zero.
- Tax-included receipts: the printed included-tax amount.
- Empty if no tax is shown at all.

## Total
- Final amount paid, including tax and tip, even if handwritten.
- Split payments (gift card + card): the full amount, not one part.
- Empty if no total amount is printed.

## Currency
- Three-letter code: USD, EUR, GBP, CAD.
- $ with a Canadian address = CAD.
- $ with a US address, or nothing indicating another country = USD.