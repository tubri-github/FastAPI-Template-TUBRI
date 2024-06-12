# -*- coding:utf-8 -*-
"""
@Des: api router
"""
from fastapi import APIRouter, Request, Depends, Query
from fastapi.security import APIKeyQuery
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, PlainTextResponse

from config import settings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional, Union

from core.Exception import ErrorCodes
from core.Utils import generate_response, setup_location, setup_wkt_and_map_name, setup_taxon, setup_date_range
from models.Occurrence import OccurrenceResponse, Occurrence, OccurrenceKML, OccurrenceKMLResponse
from models.TaxaResponse import TaxaResponse, TaxaNumer
from sqlalchemy.exc import SQLAlchemyError

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


# api validation
api_key_query = APIKeyQuery(name="api", auto_error=False)


async def verify_api_key(api: str = Depends(api_key_query), db: Session = Depends(get_db)):
    if not api:
        return PlainTextResponse(
            content="Invalid APIKey",
            status_code=200
        )

    query = text("""SELECT COUNT(*)  FROM dbo."ApiKey" WHERE "ApiKey" = :api_key""")
    result = db.execute(query, {"api_key": api}).scalar()

    if result == 0:
        return PlainTextResponse(
            content="Invalid APIKey",
            status_code=200
        )
    return api


@router.get("/occurrence/", response_model=OccurrenceResponse, tags=["Occurrence"])
async def occurrence_search(
        t: Optional[str] = 'Notropis',
        l: Optional[str] = None,
        c: Optional[str] = None,
        d: Optional[str] = None,
        q: Optional[str] = 'ethanol or EtOH',
        p: Optional[
            str] = 'POLYGON((-92.94140770116032 32.17747303410564,-89.86523582615962 32.400371789995546,-90.12890770116479 30.374771647554855,-93.38086082616299 30.52630678307028,-92.94140770116032 32.17747303410564))',
        m: Optional[str] = None,
        fmt: Optional[str] = 'csv',  # csv/json/txt
        att: Optional[int] = 0,  # 0-plain text;1-file
        # parameters for occurrence only
        cols: Optional[str] = None,
        num: Optional[int] = Query(None, ge=1, le=10000),
        set: Optional[int] = 1,
        hdr: Optional[int] = 1,
        db: Session = Depends(get_db),
        api: str = Depends(verify_api_key)):
    # Validate input parameters
    l = setup_location(l)
    d = setup_date_range(d)
    # p, m = setup_wkt_and_map_name(p, m)
    t, taxon_strict = setup_taxon(t, db)

    query = text("""
        SELECT * FROM dbo.getf2search(
            :vtaxon, :vlocation, :vcatalognumber, :vdaterange, :vother,
            :vpoly, :vmap, :vstrict, :vstartrl, :vrlcount, :vcols, false, :vdebug
        ) LIMIT :vnum OFFSET :vset
    """)
    vstrict = False,
    vdebug = False,
    params = {
        "vtaxon": t,
        "vlocation": l,
        "vcatalognumber": c,
        "vdaterange": d,
        "vother": q,
        "vpoly": p,
        "vmap": m,
        "vstartrl": None,
        "vrlcount": None,
        "vcols": cols,
        "vstrict": vstrict,
        "vdebug": vdebug,
        "vnum": num,
        "vset": set

    }
    if isinstance(api, PlainTextResponse):
        return api

    try:
        result = db.execute(query, params)
        results = result.fetchall()
    except SQLAlchemyError as e:
        if "Polygon is not validly formatted WKT" in str(e):
            return PlainTextResponse(
                content=ErrorCodes.INV_PolygonWKT.value,
                status_code=200
            )
        return PlainTextResponse(
            content="A database error occurred.",
            status_code=200
        )

    occurrences = [
        Occurrence(
            InstitutionCode=row[0],
            CollectionCode=row[1],
            CatalogNumber=row[2],
            IndividualCount=row[3],
            ScientificName=row[4],
            Family=row[5],
            PreparationType=row[6],
            Tissues=row[7],
            Latitude=row[8],
            Longitude=row[9],
            CoordinateUncertaintyInMeters=row[10],
            HorizontalDatum=row[11],
            Country=row[12],
            StateProvince=row[13],
            County=row[14],
            Island=row[15],
            IslandGroup=row[16],
            Locality=row[17],
            VerbatimElevation=row[18],
            VerbatimDepth=row[19],
            YearCollected=row[20],
            MonthCollected=row[21],
            DayCollected=row[22],
            Collector=row[23],
            GeorefMethod=row[24],
            LatLongComments=row[25],
            BasisOfRecord=row[26],
            Remarks=row[27],
            DateLastModified=row[28],
        ) for row in results
    ]
    if fmt.lower() == 'json':
        return OccurrenceResponse(occurrences=occurrences)
    return generate_response(occurrences, Occurrence, fmt, att, hdr)


@router.get("/taxa/", response_model=TaxaResponse, tags=["Taxa"])
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
        db: Session = Depends(get_db)):
    query = text("""
        SELECT * FROM dbo.getf2taxon(
            :vtaxon, :vlocation, :vcatalognumber, :vdaterange, :vother,
            :vpoly, :vmap, :vstrict,:vdebug
        )
    """)
    vstrict = False,
    vdebug = False,
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
    try:
        result = db.execute(query, params)
        results = result.fetchall()
    except SQLAlchemyError as e:
        if "Polygon is not validly formatted WKT" in str(e):
            return PlainTextResponse(
                content=ErrorCodes.INV_PolygonWKT.value,
                status_code=200
            )
        return PlainTextResponse(
            content="A database error occurred.",
            status_code=200
        )
    taxas = [
        TaxaNumer(
            ScientificName=row[0],
            NumRecords=row[1]
        ) for row in results
    ]
    if fmt.lower() == 'json':
        return TaxaResponse(taxas=taxas)
    return generate_response(taxas, TaxaNumer, fmt, att, hdr=1)
