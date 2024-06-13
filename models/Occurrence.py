from pydantic import BaseModel
from typing import List, Optional


class Occurrence(BaseModel):
    InstitutionCode: Optional[str]
    CollectionCode: Optional[str]
    CatalogNumber: Optional[str]
    IndividualCount: Optional[str]
    ScientificName: Optional[str]
    Family: Optional[str]
    PreparationType: Optional[str]
    Tissues: Optional[str]
    Latitude: Optional[str]
    Longitude: Optional[str]
    CoordinateUncertaintyInMeters: Optional[str]
    HorizontalDatum: Optional[str]
    Country: Optional[str]
    StateProvince: Optional[str]
    County: Optional[str]
    Island: Optional[str]
    IslandGroup: Optional[str]
    Locality: Optional[str]
    VerbatimElevation: Optional[str]
    VerbatimDepth: Optional[str]
    YearCollected: Optional[str]
    MonthCollected: Optional[str]
    DayCollected: Optional[str]
    Collector: Optional[str]
    GeorefMethod: Optional[str]
    LatLongComments: Optional[str]
    BasisOfRecord: Optional[str]
    Remarks: Optional[str]
    DateLastModified: Optional[str]


class OccurrenceKML(BaseModel):
    institutionCode: Optional[str]
    catalogNumber: Optional[str]
    individualCount: Optional[str]
    scientificName: Optional[str]
    latitude: Optional[str]
    longitude: Optional[str]
    monthCollected: Optional[str]
    dayCollected: Optional[str]
    yearCollected: Optional[str]


class OccurrenceResponse(BaseModel):
    occurrences: List[Occurrence]
    total: int


class OccurrenceKMLResponse(BaseModel):
    occurrences: List[OccurrenceKML]
