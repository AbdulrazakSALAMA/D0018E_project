
import hashlib
import re
from jsql import sql
import jwt
import os
from datetime import datetime, timedelta
from domain.utils.configs import get_config
from domain.utils.enums import ConfigKey, MessageCode

from domain.utils.general import generate_random_string

# ToDo
TOKENS_SECRET = os.getenv("TOKEN_SECRET", "development secret")
REFRESH_TOKENS_SECRET = os.getenv("REFRESH_TOKENS_SECRET", "development secret 2")
TOKEN_ENCODING_ALGORITHM = "HS256"
SALT_LENGTH = 5

ACCESS_TOKEN_EXPIRATIONS_HOURS = {
    "customer": get_config(ConfigKey.CUSTOMER_ACCESS_TOKEN_EXP_HOURS),
    "manager": get_config(ConfigKey.MANAGER_ACCESS_TOKEN_EXP_HOURS),
    "admin": get_config(ConfigKey.ADMIN_ACCESS_TOKEN_EXP_HOURS)
}

REFRESH_TOKEN_EXPIRATIONS_DAYS = {
    "customer": get_config(ConfigKey.CUSTOMER_REFRESH_TOKEN_EXP_DAYS),
    "manager": get_config(ConfigKey.MANAGER_REFRESH_TOKEN_EXP_DAYS),
    "admin": get_config(ConfigKey.ADMIN_REFRESH_TOKEN_EXP_DAYS)
}



def _hash_password_with_salt(password, salt):
    str = f"{password}{salt}".encode('utf-8')
    return hashlib.sha3_256(str).hexdigest()

def is_strong_password(password: str, role: str = "customer"):
    # ToDo: modify
    if role == "customer":
        return not (
            len(password) < 5
        )
    else:
        return not (
            len(password) < 5
            # or re.search(r"\d", password) is None
            # or re.search(r"[A-Z]", password) is None
            # or re.search(r"[a-z]", password) is None
        )

def validate_password(provided_password, stored_password_hash, salt):
    provided_password_hash = _hash_password_with_salt(provided_password, salt)
    return stored_password_hash == provided_password_hash

def hash_password_and_get_salt(password):
    salt = generate_random_string(SALT_LENGTH)
    password_hash = _hash_password_with_salt(password, salt)
    return password_hash, salt

def _get_expiration_time_hours(role: str = "customer", is_refresh_token: bool = False):
    assert role in ["customer", "worker", "manager", "admin"], "invalid role"
    if is_refresh_token: return REFRESH_TOKEN_EXPIRATIONS_DAYS[role] * 24
    else: return ACCESS_TOKEN_EXPIRATIONS_HOURS[role]


def generate_token(conn, user_id: int, *, role: str = "customer", expiration_time_hours = None, is_refresh_token = False):
    exp_hours = expiration_time_hours or _get_expiration_time_hours(role, is_refresh_token)
    expiration = datetime.utcnow() + timedelta(hours=exp_hours)
    secret = REFRESH_TOKENS_SECRET if is_refresh_token else TOKENS_SECRET
    payload = {
        "id": user_id,
        "exp": expiration
    }
    token = jwt.encode(payload, secret, algorithm=TOKEN_ENCODING_ALGORITHM)
    if is_refresh_token: _insert_refresh_token_in_db(conn, user_id, token)
    return token


def validate_token_and_get_payload(token, conn = None, *, is_refresh_token = False):
    assert token
    secret = REFRESH_TOKENS_SECRET if is_refresh_token else TOKENS_SECRET
    payload = jwt.decode(token, secret, algorithms=TOKEN_ENCODING_ALGORITHM)
    user_id = payload.get("id", None)
    assert type(user_id) == int
    if is_refresh_token: assert _check_refresh_token_in_db(conn, user_id, token)
    return {
        "id": user_id
    }

def _check_refresh_token_in_db(conn, user_id: int, refresh_token: str):
    found = sql(
        conn,
        f"""
            SELECT COUNT(*)
            FROM `refresh_token`
            WHERE `user_id` = :user_id
                AND `token` = :refresh_token
        """,
        user_id = user_id,
        refresh_token = refresh_token
    ).scalar()
    return found == 1

def _insert_refresh_token_in_db(conn, user_id: int, refresh_token: str):
    sql(
        conn,
        f"""
            INSERT INTO `refresh_token` (`token`, `user_id`)
            VALUES (:refresh_token, :user_id)
        """,
        user_id = user_id,
        refresh_token = refresh_token
    )

