# -*- coding:utf-8 -*-
"""
@Des: utils
"""

import hashlib
import random
import uuid
from passlib.handlers.pbkdf2 import pbkdf2_sha256


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