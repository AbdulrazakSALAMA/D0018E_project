
import json
import random
import string
import re
import os
from pydantic import BaseModel
from jsql import sql
from domain.utils.enums import UserType

import pandas as pd

EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
DEPLOYMENT_VERSION = os.getenv("DEPLOYMENT_VERSION", "0.1.0")
ROOT_DIR = os.path.abspath(os.curdir)
TEMP_FILES_DIR = f"{ROOT_DIR}/temp_media"
CREDENTIALS_FILE = f'{ROOT_DIR}/credentials.json'
ALLOWED_COUNTRY_CODES = os.getenv("ALLOWED_COUNTRY_CODES", "971,963").split(",")

ENV = os.getenv("ENV", "dev")

def generate_random_string(length: int):
    return ''.join(random.choices(string.ascii_letters, k=length))

# keys = {'k1', 'k2'}
# obj = {'k1': 1, 'k2': 2, 'k3': 3} => {'k1': 1, 'k2': 2}
def get_partial_object(obj, keys):
    return {key: obj[key] for key in obj.keys() & keys}


def compare_objects_on_keys(obj1, obj2, keys):
    assert get_partial_object(obj1, keys) == get_partial_object(obj2, keys)


def compare_objects_on_common_keys(obj1, obj2):
    common_keys = obj1.keys() & obj2.keys()
    compare_objects_on_keys(obj1, obj2, common_keys)

def is_valid_email(email: str):
    return re.fullmatch(EMAIL_REGEX, email)
    
def is_valid_phone_number(phone_number: str):
    split = phone_number.split("-")
    if len(split) != 2: return False
    country_code, local_phone_number = split[0], split[1]
    if country_code not in ALLOWED_COUNTRY_CODES: return False
    return country_code.isdigit() and local_phone_number.isdigit() and len(local_phone_number) == 9

def base_model_to_dict(obj):
    return json.loads(obj.json())

    






class UserInfo(BaseModel):
    id: int
    role: str = "customer"
    lang: str

def get_user_info(request, role = "customer"):
    return UserInfo(
        id = request.state.current_user["id"],
        role = role,
        lang = request.state.current_user["lang"]
    )


class ManagerInfo(BaseModel):
    id: int
    is_company_owner: bool
    company_id: int = None
    company_permissions: str = None
    valet_point_permissions: str = None
    managed_valet_points: str = None

def get_manager_info(conn, manager_id):
    data = sql(
        conn,
        "SELECT * FROM `manager` WHERE `user_id` = :user_id",
        user_id = manager_id,
    ).dict()
    return None if not data else ManagerInfo(
        id = data["user_id"],
        is_company_owner = data["is_company_owner"],
        company_id = data["company_id"],
        company_permissions = data["company_permissions"],
    )


class CustomerInfo(BaseModel):
    id: int
    

def get_customer_info(conn, customer_id):
    data = sql(
        conn,
        "SELECT COUNT() FROM `customer` WHERE `user_id` = :user_id",
        user_id = customer_id,
    ).dict()
    return None if not data else CustomerInfo(
        id = data["user_id"]
    )


def generate_random_code(digits: int):
    return random.randint(10**(digits-1), 10**digits-1)