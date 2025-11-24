import requests
import allure
import json
from services.favorites.endpoints import Endpoints
from services.favorites.payloads import Payloads
from services.favorites.models.favorite_model import FavoriteModel
from config.headers import Headers
from utils.helper import Helper


class FavoritesAPI(Helper):
    def __init__(self):
        super().__init__()
        self.endpoints = Endpoints()
        self.payloads = Payloads()

    @allure.step("Create favorite place")
    def create_favorite(self, title: str, lat: float, lon: float, color: str = None, token: str = None):
        payload = self.payloads.create_favorite(title, lat, lon, color)
        headers = Headers.with_token(token) if token else {}

        with allure.step(f"Создание места '{title[:50]}{'...' if len(title) > 50 else ''}'"):
            allure.attach(str(payload), name="Request Payload", attachment_type=allure.attachment_type.TEXT)

            try:
                response = requests.post(
                    url=self.endpoints.CREATE_FAVORITE,
                    data=payload,
                    headers=headers,
                    timeout=10
                )
            except requests.exceptions.Timeout:
                allure.attach("Request timeout after 10 seconds", name="Timeout Error")
                raise Exception("Request timeout")

            allure.attach(
                f"Status: {response.status_code}\nHeaders: {dict(response.headers)}\nBody: {response.text}",
                name="Raw Response",
                attachment_type=allure.attachment_type.TEXT
            )

            if response.status_code == 200:
                try:
                    favorite_data = response.json()
                    return FavoriteModel(**favorite_data)
                except ValueError as e:
                    allure.attach(f"JSON decode error: {e}\nResponse text: {response.text}",
                                  name="JSON Parse Error")
                    raise Exception(f"Failed to parse response JSON: {e}")
            else:
                error_info = {
                    "status_code": response.status_code,
                    "response_text": response.text,
                    "request_payload": payload
                }
                allure.attach(json.dumps(error_info, indent=2, ensure_ascii=False),
                              name="Error Details",
                              attachment_type=allure.attachment_type.JSON)
                return error_info