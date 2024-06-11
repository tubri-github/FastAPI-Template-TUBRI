# -*- coding:utf-8 -*-
"""
@Des: api router
"""
from fastapi import APIRouter, Request,Depends
from config import settings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from models.Occurrence import OccurrenceResponse,Occurrence
from models.TaxaResponse import TaxaResponse,TaxaNumer



router = APIRouter()

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# vlocation: Optional[str] = None,
# vcatalognumber: Optional[str] = None,
# vdaterange: Optional[str] = None,
# vother: Optional[str] = None,
# vpoly: Optional[str] = None,
# vmap: Optional[str] = None,
# vstrict: bool = False,
# vstartrl: Optional[int] = None,
# vrlcount: Optional[int] = None,
# vcols: Optional[str] = None,
# voutputtype: bool = False,
# vdebug: bool = False, db: Session = Depends(get_db)):

@router.get("/occurrence/",response_model=OccurrenceResponse,tags=["Occurrence"])
async def occurrence_search(
    t: Optional[str] = None,
    l: Optional[str] = None,
    c: Optional[str] = None,
    d: Optional[str] = None,
    q: Optional[str] = None,
    p: Optional[str] = None,
    m: Optional[str] = None,
    fmt: Optional[str] = None,
    att: Optional[str] = None,
    vstrict: bool = False,
    vstartrl: Optional[int] = None,
    vrlcount: Optional[int] = None,
    vcols: Optional[str] = None,
    voutputtype: bool = False,
    vdebug: bool = False, db: Session = Depends(get_db)):
    query = text("""
        SELECT * FROM dbo.getf2search(
            :vtaxon, :vlocation, :vcatalognumber, :vdaterange, :vother,
            :vpoly, :vmap, :vstrict, :vstartrl, :vrlcount, :vcols, :voutputtype, :vdebug
        )
    """)
    params = {
        "vtaxon": t,
        "vlocation": l,
        "vcatalognumber": c,
        "vdaterange": d,
        "vother": q,
        "vpoly": p,
        "vmap": m,
        "vstrict": vstrict,
        "vstartrl": vstartrl,
        "vrlcount": vrlcount,
        "vcols": vcols,
        "voutputtype": voutputtype,
        "vdebug": vdebug
    }
    result = db.execute(query, params)
    results = result.fetchall()
    occurrences = [
        Occurrence(
            institutionCode=row[0],
            collectionCode=row[1],
            catalogNumber=row[2],
            individualCount=row[3],
            scientificName=row[4],
            family=row[5],
            preparationType=row[6],
            tissues=row[7],
            latitude=row[8],
            longitude=row[9],
            coordinateUncertaintyInMeters=row[10],
            horizontalDatum=row[11],
            country=row[12],
            stateProvince=row[13],
            county=row[14],
            island=row[15],
            islandGroup=row[16],
            locality=row[17],
            verbatimElevation=row[18],
            verbatimDepth=row[19],
            yearCollected=row[20],
            monthCollected=row[21],
            dayCollected=row[22],
            collector=row[23],
            georefMethod=row[24],
            latLongComments=row[25],
            basisOfRecord=row[26],
            remarks=row[27],
            dateLastModified=row[28],
        ) for row in results
    ]
    return OccurrenceResponse(occurrences=occurrences)

@router.get("/taxa/",response_model=TaxaResponse,tags=["Taxa"])
async def taxa_num(
    t: Optional[str] = None,
    l: Optional[str] = None,
    c: Optional[str] = None,
    d: Optional[str] = None,
    q: Optional[str] = None,
    p: Optional[str] = None,
    m: Optional[str] = None,
    fmt: Optional[str] = None,
    att: Optional[str] = None,
    vstrict: bool = False,
    vdebug: bool = False, db: Session = Depends(get_db)):
    query = text("""
        SELECT * FROM dbo.getf2taxon(
            :vtaxon, :vlocation, :vcatalognumber, :vdaterange, :vother,
            :vpoly, :vmap, :vstrict,:vdebug
        )
    """)
    params = {
        "vtaxon": t,
        "vlocation": l,
        "vcatalognumber": c,
        "vdaterange": d,
        "vother": q,
        "vpoly": p,
        "vmap": m,
        "vstrict": vstrict,
        "vdebug": vdebug
    }
    result = db.execute(query, params)
    results = result.fetchall()
    taxas = [
        TaxaNumer(
            ScientificName=row[0],
            NumRecords=row[1]
        ) for row in results
    ]
    return TaxaResponse(taxas=taxas)