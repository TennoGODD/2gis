import requests
import allure
from services.favorites.endpoints import Endpoints
from utils.helper import Helper

class AuthAPI(Helper):
    def __init__(self):
        super().__init__()
        self.endpoints = Endpoints()

    @allure.step("Get auth token")
    def get_token(self):
        response = requests.post(self.endpoints.AUTH_TOKENS)
        assert response.status_code == 200, f"Failed to get token: {response.text}"
        token = response.cookies.get("token")
        self.attach_response({"token": token, "status_code": response.status_code})
        return token