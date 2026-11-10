from typing import Optional
from pydantic import BaseModel, Field

class Receipt(BaseModel):
    vendor: Optional[str] = Field(None, description="Business name as printed")
    date: Optional[str] = Field(None, description="Purchase date as YYYY-MM-DD")
    subtotal: Optional[float] = Field(None, description="Amount before tax")
    tax: Optional[float] = Field(None, description="Tax amount")
    total: Optional[float] = Field(None, description="Final amount paid, including tax and tip")
    currency: Optional[str] = Field(None, description="3-letter code such as USD")