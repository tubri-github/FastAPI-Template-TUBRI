from pydantic import BaseModel
from typing import List, Optional


class TaxaNumer(BaseModel):
    ScientificName: Optional[str]
    NumRecords: Optional[int]


class TaxaResponse(BaseModel):
    taxas: List[TaxaNumer]
    total:int
