
import pytest
import time

from domain.auth.security import *
from domain.utils.general import compare_objects_on_keys

PASSWORD_1 = "test password 1"
SALT_1 = "salt 1"
PASSWORD_HASH_1 = "0332a4f1a5ffa258b7cb99f6a82181bacd7ea5d4b4c2b42ad996530c9e7cc188"

PASSWORD_2 = "test password 2"
SALT_2 = "salt 2"
PASSWORD_HASH_2 = "676ebe27d0d78fca7fcb54eccfb230a7ac9b50c4a9c5e3ac52872b1e99742c95"

USER_ID_1 = 1022

def test_validate_password__success():
    validate_password(PASSWORD_1, PASSWORD_HASH_1, SALT_1)
    
    assert not validate_password(PASSWORD_1, PASSWORD_HASH_1, SALT_2)

    assert not validate_password(PASSWORD_2, PASSWORD_HASH_1, SALT_1)
    
    validate_password(PASSWORD_2, PASSWORD_HASH_2, SALT_2)


def test_hash_password_and_get_salt():
    _, salt = hash_password_and_get_salt(PASSWORD_1)
    assert len(salt) == SALT_LENGTH


def test_token__success():
    token = generate_token(USER_ID_1)
    decoded_token = validate_token_and_get_payload(token)
    obj = {
        'id': USER_ID_1
    }
    compare_objects_on_keys(decoded_token, obj, {'id'})


def test_token__invalid():
    token = generate_token(USER_ID_1)
    with pytest.raises(Exception):
        validate_token_and_get_payload(token, token_secret="wrong secret")

def test_token__expired():
    token = generate_token(USER_ID_1, expiration_time_hours=-1)
    with pytest.raises(jwt.exceptions.ExpiredSignatureError):
        validate_token_and_get_payload(token)

