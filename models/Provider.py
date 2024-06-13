from pydantic import BaseModel
from typing import List, Optional


class ProviderCitation(BaseModel):
    InstitutionCode: Optional[str]
    Institution: Optional[str]
    NumRecords: Optional[int]


class ProviderResponse(BaseModel):
    providers: List[ProviderCitation]
    total: int
