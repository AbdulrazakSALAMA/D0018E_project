from fastapi import status
from domain.auth.security import validate_token_and_get_payload
from domain.utils import test_utils as tutils
import jwt

client = tutils.TEST_CLIENT


def _validate_response_token_test(response):
    token = str(response.json())
    payload = validate_token_and_get_payload(token)
    assert type(payload["id"]) == int


def test_init():
    tutils.reset_db()


def test_register():
    response = client.post(
        "/auth/register/",
        json={"username": "Customer1", "password": "Customer1"}
    )
    assert response.status_code == status.HTTP_200_OK
    _validate_response_token_test(response)
    
    response = client.post(
        "/auth/register/",
        json={"username": "customer1", "password": "customer1"}
    )
    assert response.status_code == status.HTTP_200_OK
    _validate_response_token_test(response)

    response = client.post(
        "/auth/register/",
        json={"username": "customer1", "password": "customer1"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login():
    response = client.post(
        "/auth/login",
        json={"username": "customer1", "password": "customer1"}
    )
    assert response.status_code == status.HTTP_200_OK
    _validate_response_token_test(response)
    
    response = client.post(
        "/auth/login",
        json={"username": "customer1", "password": "user2"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    response = client.post(
        "/auth/login",
        json={"username": "Customer1", "password": "customer1"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    response = client.post(
        "/auth/login",
        json={"username": "Customer1", "password": "Customer1"}
    )
    assert response.status_code == status.HTTP_200_OK
    _validate_response_token_test(response)



