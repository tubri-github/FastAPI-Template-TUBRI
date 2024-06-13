from pydantic import BaseModel
from typing import List, Optional


class Location(BaseModel):
    Country: Optional[str]
    StateProvince: Optional[str]
    County: Optional[str]
    Locality: Optional[str]
    Latitude: Optional[str]
    Longitude: Optional[str]
    NumRecords: Optional[int]


class LocationResponse(BaseModel):
    locations: List[Location]
