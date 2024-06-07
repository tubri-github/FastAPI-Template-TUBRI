# -*- coding:utf-8 -*-
"""
@Des: api router
"""
from fastapi import APIRouter, Request,Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from pydantic import BaseModel
from models.Occurrence import OccurrenceResponse,Occurrence



router = APIRouter()

DATABASE_URL = "postgresql://postgres:p@localhost:5432/fn2"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class SearchParams(BaseModel):
    vtaxon: Optional[str] = None
    vlocation: Optional[str] = None
    vcatalognumber: Optional[str] = None
    vdaterange: Optional[str] = None
    vother: Optional[str] = None
    vpoly: Optional[str] = None
    vmap: Optional[str] = None
    vstrict: bool = False
    vstartrl: Optional[int] = None
    vrlcount: Optional[int] = None
    vcols: Optional[str] = None
    voutputtype: bool = False
    vdebug: bool = False

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/occurrence/",response_model=OccurrenceResponse,tags=["Occurrence"])
async def occurrence_search(vtaxon: Optional[str] = None,
    vlocation: Optional[str] = None,
    vcatalognumber: Optional[str] = None,
    vdaterange: Optional[str] = None,
    vother: Optional[str] = None,
    vpoly: Optional[str] = None,
    vmap: Optional[str] = None,
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
        "vtaxon": vtaxon,
        "vlocation": vlocation,
        "vcatalognumber": vcatalognumber,
        "vdaterange": vdaterange,
        "vother": vother,
        "vpoly": vpoly,
        "vmap": vmap,
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


# api_router.post("/test/oath2", tags=["测试oath2授权"])(test_oath2)
# api_router.include_router(user.router, prefix='/admin', tags=["用户管理"])
# api_router.include_router(role.router, prefix='/admin', tags=["角色管理"])
# api_router.include_router(access.router, prefix='/admin', tags=["权限管理"])
# api_router.include_router(websocket.router, prefix='/ws', tags=["WebSocket"])
# api_router.include_router(wechat.router, prefix='/wechat', tags=["微信授权"])
# api_router.include_router(sms.router, prefix='/sms', tags=["短信接口"])
# api_router.include_router(cos.router, prefix='/cos', tags=["对象存储接口"])
