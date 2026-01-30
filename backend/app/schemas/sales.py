from datetime import date
from typing import List, Optional
from pydantic import BaseModel, RootModel, PositiveInt, NonNegativeFloat, ConfigDict

class SaleItem(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    date: date
    item: str
    quantity: PositiveInt
    price: NonNegativeFloat
    total: Optional[float] = None
    category: Optional[str] = None

class SalesBatch(RootModel):
    root: List[SaleItem]
