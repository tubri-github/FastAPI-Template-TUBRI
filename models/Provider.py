from pydantic import BaseModel
from typing import List, Optional


class ProviderCitation(BaseModel):
    InstitutionCode: Optional[str]
    Institution: Optional[str]
    NumRecords: Optional[int]


class ProviderDetails(BaseModel):
    Institution: Optional[str]
    Status: Optional[str]
    Cached: Optional[int]
    Declared: Optional[int]
    Skipped: Optional[int]
    ResourceName: Optional[str]


class ProviderResponse(BaseModel):
    providers: List[ProviderCitation]
    total: int


class ProviderListResponse(BaseModel):
    providers: List[ProviderDetails]
    total: int
