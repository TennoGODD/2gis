import pytest
import requests
from services.favorites.endpoints import Endpoints
from utils.helper import Helper


class TestSetup(Helper):

    def __init__(self):
        super().__init__()
        self.endpoints = Endpoints()

    def get_fresh_token(self):
        response = requests.post(self.endpoints.AUTH_TOKENS)
        token = response.cookies.get("token")
        self.attach_response({
            "token_request": {"url": self.endpoints.AUTH_TOKENS, "method": "POST"},
            "token_response": {"token": token, "status_code": response.status_code}
        })
        return token


@pytest.fixture(scope="session")
def test_setup():
    return TestSetup()


@pytest.fixture
def fresh_token(test_setup):
    return test_setup.get_fresh_token()


@pytest.fixture
def favorite_payloads():
    return {
        "valid": {
            "title": "Тестовое место",
            "lat": 55.7558,
            "lon": 37.6176
        },
        "with_color": {
            "title": "Место с цветом",
            "lat": 55.7558,
            "lon": 37.6176,
            "color": "GREEN"
        },
        "long_title": {
            "title": "Т" * 1000,
            "lat": 55.7558,
            "lon": 37.6176
        },
        "short_title": {
            "title": "Т",
            "lat": 55.7558,
            "lon": 37.6176
        },
        "lowercase_color": {
            "title": "Место с цветом в нижнем регистре",
            "lat": 55.7558,
            "lon": 37.6176,
            "color": "red"
        },
        "empty_title": {
            "title": "",
            "lat": 55.7558,
            "lon": 37.6176
        },
        "zero_coordinates": {
            "title": "Нулевые координаты",
            "lat": 0.0,
            "lon": 0.0
        },
        "special_chars": {
            "title": "Место с символами: 123, test, точка.",
            "lat": 55.7558,
            "lon": 37.6176
        }
    }