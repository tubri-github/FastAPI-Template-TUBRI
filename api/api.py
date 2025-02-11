# -*- coding:utf-8 -*-
"""
@Des: api router
"""
from fastapi import APIRouter, Request, Depends, Query
from fastapi.security import APIKeyQuery, HTTPAuthorizationCredentials, HTTPBearer
import jwt
from datetime import datetime, timedelta
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, PlainTextResponse

from config import settings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional

from core.Exception import ErrorCodes
from core.Utils import generate_response, setup_location, setup_wkt_and_map_name, setup_taxon, setup_date_range
from models.Occurrence import OccurrenceResponse, Occurrence
from models.TaxaResponse import TaxaResponse, TaxaNumer
from models.Provider import ProviderResponse, ProviderCitation, ProviderDetails, ProviderListResponse
from models.Location import LocationResponse, Location
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix='/v1')

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# front-end JWT
SECRET_KEY = "Fishnet2_L*A"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15


# generate JWT
def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# verify JWT
def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid Token")


@router.get("/clients")
async def get_jwt_token():
    # return a jwt token for the clients
    token_data = {"sub": "frontend_access"}
    token = create_jwt_token(token_data)
    return {"token": token}


# reular user api validation

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


async def authenticate_request(
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
        api: str = Depends(api_key_query),
        db: Session = Depends(get_db)
):
    # 尝试 JWT 验证
    if credentials:
        token = credentials.credentials
        try:
            return verify_jwt(token)
        except HTTPException:
            pass  # 如果 JWT 验证失败，继续检查 API Key

    # 尝试 API Key 验证
    if api:
        query = text("""SELECT COUNT(*) FROM dbo."ApiKey" WHERE "ApiKey" = :api_key""")
        result = db.execute(query, {"api_key": api}).scalar()
        if result > 0:
            return {"sub": "apikey_access"}

    # 两种验证都失败
    raise HTTPException(status_code=403, detail="Authentication failed")


@router.get("/occurrence/", response_model=OccurrenceResponse, tags=["Occurrence"],
            dependencies=[Depends(authenticate_request)])
async def occurrence_search(
        t: Optional[str] = None,  # 'Notropis',
        l: Optional[str] = None,
        c: Optional[str] = None,
        d: Optional[str] = None,
        q: Optional[str] = None,  # 'ethanol or EtOH',
        p: Optional[
            str] = None,
        # 'POLYGON((-92.94140770116032 32.17747303410564,-89.86523582615962 32.400371789995546,-90.12890770116479 30.374771647554855,-93.38086082616299 30.52630678307028,-92.94140770116032 32.17747303410564))',
        m: Optional[str] = None,
        fmt: Optional[str] = Query("csv", enum=["csv", "txt", "kml"]),  # csv/json/txt
        att: Optional[int] = 0,  # 0-plain text;1-file
        # parameters for occurrence only
        cols: Optional[str] = None,
        num: Optional[int] = Query(None, ge=1, le=10000),
        set: Optional[int] = 1,
        hdr: Optional[int] = 1,
        db: Session = Depends(get_db),
        api: str = Depends(verify_api_key)):
    # Validate input parameters
    # l = setup_location(l)
    d = setup_date_range(d)
    # p, m = setup_wkt_and_map_name(p, m)
    t, taxon_strict = setup_taxon(t, db)

    paging_string = ""
    if num is not None:
        paging_string = f" LIMIT {num} OFFSET {set - 1} * {num}"

    query = f"""SELECT *,COUNT(*) OVER() AS total_count FROM dbo.getf2search(
            :vtaxon, :vlocation, :vcatalognumber, :vdaterange, :vother,
            :vpoly, :vmap, :vstrict, :vstartrl, :vrlcount, :vcols, false, :vdebug
        ) ORDER BY catalognumber {paging_string}
    """
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
        "vdebug": vdebug

    }
    # if isinstance(api, PlainTextResponse):
    #     return api

    try:
        result = db.execute(text(query), params)
        results = result.fetchall()
    except SQLAlchemyError as e:
        error_message = str(e)
        if "Polygon is not validly formatted WKT" in str(e):
            return PlainTextResponse(
                content=ErrorCodes.INV_PolygonWKT.value,
                status_code=200
            )
        return PlainTextResponse(
            content=f"A database error occurred.{error_message}",
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
    total_count = 0
    if len(results) > 0:
        total_count = results[0][29]
    if fmt.lower() == 'json':
        return OccurrenceResponse(occurrences=occurrences, total=total_count)
    return generate_response(occurrences, Occurrence, fmt, att, hdr)


@router.get("/taxa/", response_model=TaxaResponse, tags=["Taxa"], dependencies=[Depends(authenticate_request)])
async def taxa_num(
        t: Optional[str] = None,
        l: Optional[str] = None,
        c: Optional[str] = None,
        d: Optional[str] = None,
        q: Optional[str] = None,
        p: Optional[str] = None,
        m: Optional[str] = None,
        num: Optional[int] = Query(None, ge=1, le=10000),
        set: Optional[int] = 1,
        fmt: Optional[str] = 'csv',  # csv/json/txt
        att: Optional[int] = 0,  # 0-plain text;1-file
        db: Session = Depends(get_db),
        api: str = Depends(verify_api_key)):
    # if isinstance(api, PlainTextResponse):
    #     return api
    paging_string = ""
    if num is not None:
        paging_string = f" LIMIT {num} OFFSET {set - 1} * {num}"

        # Validate input parameters
        # l = setup_location(l)
    d = setup_date_range(d)
    # p, m = setup_wkt_and_map_name(p, m)
    t, taxon_strict = setup_taxon(t, db)

    query = text(f"""
        SELECT *,
    COUNT(*) OVER() AS total_count FROM dbo.getf2taxon(
            :vtaxon, :vlocation, :vcatalognumber, :vdaterange, :vother,
            :vpoly, :vmap, :vstrict,:vdebug
        ){paging_string}
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
    total_count = 0
    if len(results) > 0:
        total_count = results[0][2]
    if fmt.lower() == 'json':
        return TaxaResponse(taxas=taxas, total=total_count)
    return generate_response(taxas, TaxaNumer, fmt, att, hdr=1)


@router.get("/providers/", response_model=ProviderResponse, tags=["Provider"],
            dependencies=[Depends(authenticate_request)])
async def provider_citation(
        t: Optional[str] = None,
        l: Optional[str] = None,
        c: Optional[str] = None,
        d: Optional[str] = None,
        q: Optional[str] = None,
        p: Optional[str] = None,
        m: Optional[str] = None,
        num: Optional[int] = Query(None, ge=1, le=10000),
        set: Optional[int] = 1,
        fmt: Optional[str] = 'csv',  # csv/json/txt
        att: Optional[int] = 0,  # 0-plain text;1-file
        db: Session = Depends(get_db),
        api: str = Depends(verify_api_key)):
    # if isinstance(api, PlainTextResponse):
    #     return api

    # Validate input parameters
    # l = setup_location(l)
    d = setup_date_range(d)
    # p, m = setup_wkt_and_map_name(p, m)
    t, taxon_strict = setup_taxon(t, db)

    paging_string = ""
    if num is not None:
        paging_string = f" LIMIT {num} OFFSET {set - 1} * {num}"

    query = text(f"""
        SELECT  *,
    COUNT(*) OVER() AS total_count FROM dbo.getprovidercitations_f(
            :vtaxon, :vlocation, :vcatalognumber, :vdaterange, :vother,
            :vpoly, :vmap, :vstrict,:vdebug
        ){paging_string}
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
    providers = [
        ProviderCitation(
            InstitutionCode=row[0],
            Institution=row[1],
            NumRecords=row[2]
        ) for row in results
    ]
    total_count = 0
    if len(results) > 0:
        total_count = results[0][3]
    if fmt.lower() == 'json':
        return ProviderResponse(providers=providers, total=total_count)
    return generate_response(providers, ProviderCitation, fmt, att, hdr=1)


@router.get("/providerlist/", response_model=ProviderListResponse, tags=["Provider"],
            dependencies=[Depends(authenticate_request)])
async def provider_citation(
        db: Session = Depends(get_db),
        api: str = Depends(verify_api_key)):
    query = text(f"""
        SELECT  * from dbo.getproviders();
    """)
    try:
        result = db.execute(query)
        results = result.fetchall()
    except SQLAlchemyError as e:
        return PlainTextResponse(
            content="A database error occurred.",
            status_code=200
        )
    providers = [
        ProviderDetails(
            Institution=row[0],
            Status=row[1],
            Cached=row[2],
            Declared=row[3],
            Skipped=row[4],
            ResourceName=row[5],
        ) for row in results
    ]
    total_count = 0
    if len(results) > 0:
        total_count = results[0][3]
    return ProviderListResponse(providers=providers, total=total_count)


@router.get("/locations/", response_model=LocationResponse, tags=["Location"],
            dependencies=[Depends(authenticate_request)])
async def get_location(
        t: Optional[str] = None,
        l: Optional[str] = None,
        c: Optional[str] = None,
        d: Optional[str] = None,
        q: Optional[str] = None,
        p: Optional[str] = None,
        m: Optional[str] = None,
        num: Optional[int] = Query(None, ge=1, le=10000),
        set: Optional[int] = 1,
        fmt: Optional[str] = 'csv',  # csv/json/txt
        att: Optional[int] = 0,  # 0-plain text;1-file
        db: Session = Depends(get_db),
        api: str = Depends(verify_api_key)):
    # if isinstance(api, PlainTextResponse):
    #     return api

    # Validate input parameters
    # l = setup_location(l)
    d = setup_date_range(d)
    # p, m = setup_wkt_and_map_name(p, m)
    t, taxon_strict = setup_taxon(t, db)

    paging_string = ""
    if num is not None:
        paging_string = f" LIMIT {num} OFFSET {set - 1} * {num}"

    query = text(f"""
        SELECT  *,
    COUNT(*) OVER() AS total_count FROM dbo.getlocations(
            :vtaxon, :vlocation, :vcatalognumber, :vdaterange, :vother,
            :vpoly, :vmap, :vstrict,:vdebug
        ){paging_string}
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
    locations = [
        Location(
            Country=row[0],
            StateProvince=row[1],
            County=row[2],
            Locality=row[3],
            Latitude=row[4],
            Longitude=row[5],
            NumRecords=row[6],
        ) for row in results
    ]
    total_count = 0
    if len(results) > 0:
        total_count = results[0][7]
    if fmt.lower() == 'json':
        return LocationResponse(locations=locations, total=total_count)
    return generate_response(locations, Location, fmt, att, hdr=1)
