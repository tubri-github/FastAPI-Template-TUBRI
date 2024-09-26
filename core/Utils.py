# -*- coding:utf-8 -*-
"""
@Des: utils
"""

import hashlib
import random
import re
import uuid
from passlib.handlers.pbkdf2 import pbkdf2_sha256

import csv
import io
from datetime import datetime
from typing import List, Type, Optional, Tuple
from fastapi.responses import PlainTextResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from starlette.exceptions import HTTPException

from fastapi.responses import StreamingResponse

from models.Occurrence import Occurrence


async def kml_generator(data):
    yield '<?xml version="1.0" encoding="UTF-8"?>\n'
    yield '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
    yield '<Document>\n'

    # Add Styles
    yield """
    <Style id="normalState">
        <IconStyle>
            <scale>.6</scale>
            <Icon>
                <href>http://www.museum.tulane.edu/nelson/arrow.png</href>
            </Icon>
        </IconStyle>
        <LabelStyle>
            <scale>0</scale>
        </LabelStyle>
    </Style>
    <Style id="highlightState">
        <IconStyle>
            <Icon>
                <href>http://www.museum.tulane.edu/nelson/arrow.png</href>
            </Icon>
            <scale>1.0</scale>
        </IconStyle>
        <LabelStyle>
            <scale>1.0</scale>
        </LabelStyle>
    </Style>
    <StyleMap id="s1">
        <Pair>
            <key>normal</key>
            <styleUrl>#normalState</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#highlightState</styleUrl>
        </Pair>
    </StyleMap>
    """

    for item in data:
        if item.Longitude is not '' and item.Latitude is not '':
            yield '<Placemark>\n'
            yield f'<name>{item.InstitutionCode} {item.CatalogNumber}</name>\n'
            yield '<description>\n'
            yield '<![CDATA[\n'
            yield f'{item.InstitutionCode} {item.CatalogNumber}<br/>\n'
            yield f'<i>{item.ScientificName}</i><br/>\n'
            yield f'No. specimens: {item.IndividualCount}<br/>\n'
            yield f'{item.Locality}; {item.County}; {item.StateProvince}; {item.Country}<br/>\n'
            yield f'Collected by: {item.Collector}<br/>\n'
            yield f'Year collected: {item.YearCollected}<br/>\n'
            yield f'Month collected: {item.MonthCollected}<br/>\n'
            yield f'Day collected: {item.DayCollected}<br/>\n'
            yield f'<br/><a href="http://www.fishnet2.net/reporterror.aspx?InsCode={item.InstitutionCode}&CatNo={item.CatalogNumber}&SciName={item.ScientificName}">Wrong location or other problem? Click here to report it.</a><br/>\n'
            yield ']]>\n'
            yield '</description>\n'
            yield '<styleUrl>#s1</styleUrl>\n'
            yield '<Point>\n'
            yield f'<coordinates>{item.Longitude},{item.Latitude}</coordinates>\n'
            yield '</Point>\n'
            yield '</Placemark>\n'

    yield '</Document>\n'
    yield '</kml>'

def generate_kml_response(data, filename=None):
    headers_dict = {'Content-Disposition': f'attachment; filename="{filename}"'} if filename else {}
    return StreamingResponse(kml_generator(data), media_type="application/vnd.google-earth.kml+xml", headers=headers_dict)


def get_csv_response(data, headers, filename=None, hasheader=True):
    output = io.StringIO()
    writer = csv.writer(output)
    if hasheader:
        writer.writerow(headers)
    writer.writerows(data)
    output.seek(0)
    headers_dict = {}
    if filename:
        headers_dict = {'Content-Disposition': f'attachment; filename="{filename}"'}
        return StreamingResponse(output, media_type='text/plain', headers=headers_dict)
    else:
        return PlainTextResponse(output.getvalue())


def get_txt_response(data, headers, filename=None, hasheader=True):
    def iter_rows():
        if hasheader:
            yield "\t".join(headers) + "\n"
        for row in data:
            yield "\t".join(map(str, row)) + "\n"

    if filename:
        headers_dict = {'Content-Disposition': f'attachment; filename="{filename}"'}
        return StreamingResponse(iter_rows(), media_type='text/plain', headers=headers_dict)
    else:
        return PlainTextResponse(iter_rows())


def generate_response(data: List[BaseModel], model: Type[BaseModel], fmt='csv', att=0, hdr=1):
    hasheader = True
    if hdr == 0:
        hasheader = False
    headers = list(model.model_fields.keys())

    # Convert data models to list of lists
    data_list = [list(item.dict().values()) for item in data]

    if att == 1:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"SearchResults-{timestamp}.{fmt.lower()}"
    else:
        filename = None

    if fmt == "csv":
        return get_csv_response(data_list, headers, filename=filename, hasheader=hasheader)
    elif fmt == "txt":
        return get_txt_response(data_list, headers, filename=filename, hasheader=hasheader)
    elif fmt == 'kml' and model == Occurrence:  # return occurrence model data list only
        return generate_kml_response(data, filename=filename)
    else:
        return PlainTextResponse("Invalid format specified", status_code=400)


def random_str():
    """
    uuid
    :return: str
    """
    only = hashlib.md5(str(uuid.uuid1()).encode(encoding='UTF-8')).hexdigest()
    return str(only)


def en_password(psw: str):
    """
    encrypt psw
    :param psw: pwd
    :return: encrypted pwd
    """
    password = pbkdf2_sha256.hash(psw)
    return password


def check_password(password: str, old: str):
    """
    psw validation
    :param password: psw from u
    :param old:
    :return: Boolean
    """
    check = pbkdf2_sha256.verify(password, old)
    if check:
        return True
    else:
        return False


def code_number(ln: int):
    """
    random number
    :param ln: length
    :return: str
    """
    code = ""
    for i in range(ln):
        ch = chr(random.randrange(ord('0'), ord('9') + 1))
        code += ch

    return code


class ErrorCodes:
    INV_PolyFormat = "invalid polygon format"
    INV_MinTerms = "at least one term required"
    INV_DateRangeFromat = "invalid date range"
    INV_MapName = "invalid map name"
    INV_PolygonWKT = "Polygon is not validly formatted WKT"


def setup_location(location: Optional[str]) -> Optional[str]:
    if location:
        location = re.sub(r"\s+,", ",", location)
        location = re.sub(r",", ", ", location)
        location = re.sub(r"\s+:", ":", location)
        location = re.sub(r":\s+", ":", location)
        location = re.sub(r"\s+;", ";", location)
        location = re.sub(r";", "; ", location)
        location = re.sub(r"\w\.", lambda m: m.group(0)[0], location)
        location = re.sub(r"\s+&", "&", location)
        location = re.sub(r"&", "& ", location)
        location = re.sub(r"[!@#\$%\^\*\(\){}\[\]|\\<>?/~`\+\=\-_]", "", location)
    return location


# data range
def setup_date_range(date_range: Optional[str]) -> Optional[str]:
    if date_range:
        if len(date_range) == 9 and re.match(r"\d{4}-\d{4}", date_range):
            return date_range
        if len(date_range) == 4 and date_range.isdigit():
            return f"{date_range}-{date_range}"
        raise HTTPException(status_code=400, detail=ErrorCodes.INV_DateRangeFromat)
    return date_range


# WKT
def setup_wkt_and_map_name(wkt: Optional[str], map_name: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    if not wkt:
        if map_name:
            if not map_name.isdigit() or int(map_name) < 1:
                raise HTTPException(status_code=400, detail=ErrorCodes.INV_MapName)
            return None, map_name
    else:
        # 假设有一个函数 is_wkt_valid 来验证 WKT 格式
        if is_wkt_valid(wkt):
            return wkt, None
        raise HTTPException(status_code=400, detail=ErrorCodes.INV_PolyFormat)
    return None, None


# taxon validation
def setup_taxon(taxon: Optional[str], db: Session) -> Tuple[Optional[str], bool]:
    taxon_strict = False
    if taxon:
        if itis_exists(db):
            common_name = check_cn_itis_lookup(taxon, db)
            if common_name:
                taxon = common_name
            else:
                scientific_name = check_sn_itis_lookup(taxon, db)
                if scientific_name:
                    taxon = scientific_name

            # Check for duplicate names to set taxon_strict
            taxon_parts = sorted(taxon.split())
            if len(set(taxon_parts)) < len(taxon_parts):
                taxon_strict = True
    return taxon, taxon_strict


def is_wkt_valid(wkt: str) -> bool:
    #
    return True


def itis_exists(db: Session) -> bool:
    sql = "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'SN_ITIS_lookup'"
    result = db.execute(text(sql)).scalar()
    return result > 0


def check_cn_itis_lookup(taxon: str, db: Session) -> Optional[str]:
    sql = "select * from dbo.getCommonName_f(:CN)"
    result = db.execute(text(sql), {"CN": taxon}).fetchone()
    return result[0] if result[0] is not None else None


def check_sn_itis_lookup(taxon: str, db: Session) -> Optional[str]:
    sql = "select * from dbo.getSynonyms_f(:SN)"
    result = db.execute(text(sql), {"SN": taxon}).fetchone()
    return result[0] if result[0] is not None else None


def has_duplicate_names(taxon: str) -> bool:
    arr_tax = taxon.split(" OR ")
    for s in arr_tax:
        arr_check = sorted(s.split())
        for i in range(1, len(arr_check)):
            if arr_check[i].upper() == arr_check[i - 1].upper():
                return True
    return False
