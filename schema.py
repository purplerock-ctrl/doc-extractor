from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Receipt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vendor: Optional[str] = Field(
        None,
        description=(
            "The business name as printed at the top of the receipt. "
            "If a different legal or company name appears elsewhere "
            "(e.g. in the footer), use the name at the top."
        ),
    )

    date: Optional[str] = Field(
        None,
        description=(
            "The purchase or invoice date, formatted as YYYY-MM-DD. "
            "Ignore due dates, pick-up or ready dates, and print times. "
            "Expand two-digit years to 20XX. "
            "For receipts from outside the US, numeric dates are usually day/month/year; "
            "use the address and currency to decide the order."
        ),
    )

    subtotal: Optional[float] = Field(
        None,
        description=(
            "The amount before tax, after any discounts or coupons, as printed. "
            "If no subtotal line is printed, return null. "
            "Never copy the total into this field and never calculate a subtotal yourself. "
            "On tax-included receipts (TTC, VAT included) with no subtotal line, return null."
        ),
    )

    tax: Optional[float] = Field(
        None,
        description=(
            "The tax amount as printed. Return 0 if a tax line shows zero. "
            "On tax-included receipts, use the printed included-tax amount "
            "(e.g. 'incl. VAT 20%' or 'dont TVA'). Return null if no tax is shown at all."
        ),
    )

    total: Optional[float] = Field(
        None,
        description=(
            "The final amount paid, including tax and tip, even if the tip and total "
            "are handwritten. If payment is split (e.g. gift card plus card), "
            "the total is the full amount before the split, not one payment."
        ),
    )

    currency: Optional[str] = Field(
        None,
        description=(
            "Three-letter ISO currency code such as USD, EUR, GBP, CAD. "
            "If only a symbol is shown, use the address to decide: "
            "$ with a Canadian address is CAD; "
            "$ with a US address, or with nothing indicating another country, is USD."
        ),
    )