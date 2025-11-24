import allure
import pytest
import requests
import time
from config.base_test import BaseTest


@allure.epic("API 2GIS")
@allure.feature("Негативные тесты избранных мест")
class TestFavoritesNegative(BaseTest):

    def setup_method(self):
        super().setup_method()

    @allure.title("01. Создание места без токена")
    @pytest.mark.order(1)
    def test_create_favorite_without_token(self):
        response = requests.post(
            url="https://regions-test.2gis.com/v1/favorites",
            data={
                "title": "Место без токена",
                "lat": 55.7558,
                "lon": 37.6176
            }
        )

        assert response.status_code in [401, 403], (
            f"Ожидался статус 401/403 без токена, но получен {response.status_code}\n"
            f"Ответ: {response.text}"
        )

    @allure.title("02. Создание места с просроченным токеном")
    @pytest.mark.order(2)
    def test_create_favorite_with_expired_token(self, fresh_token):
        time.sleep(2.1)

        response = requests.post(
            url="https://regions-test.2gis.com/v1/favorites",
            data={
                "title": "Место с просроченным токеном",
                "lat": 55.7558,
                "lon": 37.6176
            },
            cookies={"token": fresh_token}
        )

        assert response.status_code in [401, 403], (
            f"Ожидался статус 401/403 с просроченным токеном, но получен {response.status_code}\n"
            f"Ответ: {response.text}"
        )

    @allure.title("03. Создание места с невалидным токеном")
    @pytest.mark.order(3)
    def test_create_favorite_with_invalid_token(self):
        response = requests.post(
            url="https://regions-test.2gis.com/v1/favorites",
            data={
                "title": "Место с невалидным токеном",
                "lat": 55.7558,
                "lon": 37.6176
            },
            cookies={"token": "invalid_token_12345"}
        )

        assert response.status_code in [401, 403], (
            f"Ожидался статус 401/403 с невалидным токеном, но получен {response.status_code}\n"
            f"Ответ: {response.text}"
        )

    @allure.title("04. Создание места без обязательных полей")
    @pytest.mark.parametrize("missing_field", ["title", "lat", "lon"])
    @pytest.mark.order(4)
    def test_create_favorite_without_required_fields(self, fresh_token, missing_field):
        data = {
            "title": "Тестовое место",
            "lat": 55.7558,
            "lon": 37.6176
        }
        del data[missing_field]

        response = requests.post(
            url="https://regions-test.2gis.com/v1/favorites",
            data=data,
            cookies={"token": fresh_token}
        )

        assert response.status_code == 400, (
            f"Ожидался статус 400 при отсутствии {missing_field}, но получен {response.status_code}\n"
            f"Ответ: {response.text}"
        )

    @allure.title("05. Создание места с пустыми обязательными полями")
    @pytest.mark.parametrize("field,value", [
        ("title", ""),
        ("lat", ""),
        ("lon", ""),
    ])
    @pytest.mark.order(5)
    def test_create_favorite_with_empty_required_fields(self, fresh_token, field, value):
        data = {
            "title": "Тестовое место",
            "lat": 55.7558,
            "lon": 37.6176
        }
        data[field] = value

        response = requests.post(
            url="https://regions-test.2gis.com/v1/favorites",
            data=data,
            cookies={"token": fresh_token}
        )

        assert response.status_code == 400, (
            f"Ожидался статус 400 когда {field} пустое, но получен {response.status_code}\n"
            f"Ответ: {response.text}"
        )

    @allure.title("06. Создание места с невалидной длиной title")
    @pytest.mark.parametrize("length,description", [
        (0, "пустое название"),
        (1000, "1000 символов"),
        (1500, "1500 символов"),
    ])
    @pytest.mark.order(6)
    def test_create_favorite_with_invalid_title_length(self, fresh_token, length, description):
        title = "Т" * length

        response = requests.post(
            url="https://regions-test.2gis.com/v1/favorites",
            data={
                "title": title,
                "lat": 55.7558,
                "lon": 37.6176
            },
            cookies={"token": fresh_token}
        )

        assert response.status_code == 400, (
            f"Ожидался статус 400 для названия с {description}, но получен {response.status_code}\n"
            f"Длина названия: {length}\n"
            f"Ответ: {response.text}"
        )

    @allure.title("07. Создание места с запрещенными символами в названии")
    @pytest.mark.parametrize("title,description", [
        ("Title with 😊 emoji", "эмодзи"),
        ("Title with 🐍 python", "эмодзи и текст"),
        ("Title with <script>alert('xss')</script>", "HTML теги"),
    ])
    @pytest.mark.order(7)
    def test_create_favorite_with_forbidden_characters(self, fresh_token, title, description):
        response = requests.post(
            url="https://regions-test.2gis.com/v1/favorites",
            data={
                "title": title,
                "lat": 55.7558,
                "lon": 37.6176
            },
            cookies={"token": fresh_token}
        )

        assert response.status_code != 500, (
            f"Ошибка сервера 500 для названия с {description}\n"
            f"Название: {title}\n"
            f"Ответ: {response.text}"
        )

    @allure.title("08. Создание места с невалидными координатами")
    @pytest.mark.parametrize("lat,lon,description", [
        (91.0, 0.0, "широта > 90"),
        (-91.0, 0.0, "широта < -90"),
        (0.0, 181.0, "долгота > 180"),
        (0.0, -181.0, "долгота < -180"),
        (90.1, 180.1, "оба значения вне диапазона"),
        (-90.1, -180.1, "оба отрицательных значения вне диапазона"),
    ])
    @pytest.mark.order(8)
    def test_create_favorite_with_invalid_coordinates(self, fresh_token, lat, lon, description):
        response = requests.post(
            url="https://regions-test.2gis.com/v1/favorites",
            data={
                "title": f"Место с {description}",
                "lat": lat,
                "lon": lon
            },
            cookies={"token": fresh_token}
        )

        assert response.status_code == 400, (
            f"Ожидался статус 400 для {description}, но получен {response.status_code}\n"
            f"Координаты: ({lat}, {lon})\n"
            f"Ответ: {response.text}"
        )

    @allure.title("09. Создание места с невалидным цветом")
    @pytest.mark.parametrize("color,description", [
        ("PURPLE", "несуществующий цвет"),
        ("BLACK", "несуществующий цвет"),
        ("green", "нижний регистр"),
        ("Red", "смешанный регистр"),
        ("", "пустой параметр"),
        ("123", "цифры"),
        ("BLUE_GREEN", "с подчеркиванием"),
    ])
    @pytest.mark.order(9)
    def test_create_favorite_with_invalid_color(self, fresh_token, color, description):
        response = requests.post(
            url="https://regions-test.2gis.com/v1/favorites",
            data={
                "title": f"Место с цветом {description}",
                "lat": 55.7558,
                "lon": 37.6176,
                "color": color
            },
            cookies={"token": fresh_token}
        )

        assert response.status_code == 400, (
            f"Ожидался статус 400 для цвета '{color}' ({description}), но получен {response.status_code}\n"
            f"Ответ: {response.text}"
        )

    @allure.title("10. Создание места с неверными типами данных")
    @pytest.mark.parametrize("field,wrong_value,description", [
        ("lat", "fifty_five", "строка вместо числа"),
        ("lon", "invalid", "строка вместо числа"),
        ("lat", True, "булево значение вместо числа"),
        ("lon", False, "булево значение вместо числа"),
        ("title", 12345, "число вместо строки"),
        ("title", True, "булево значение вместо строки"),
        ("color", 123, "число вместо строки"),
        ("color", True, "булево значение вместо строки"),
    ])
    @pytest.mark.order(10)
    def test_create_favorite_with_wrong_data_types(self, fresh_token, field, wrong_value, description):
        data ={
            "title": "Тестовое место",
            "lat": 55.7558,
            "lon": 37.6176
        }
        data[field] = wrong_value

        response = requests.post(
            url="https://regions-test.2gis.com/v1/favorites",
            data=data,
            cookies={"token": fresh_token}
        )


        assert response.status_code == 400, (
            f"Ожидался статус 400 для {field} с {description}, но получен {response.status_code}\n"
            f"Неверное значение: {wrong_value} (тип: {type(wrong_value).__name__})\n"
            f"Ответ: {response.text}"
        )