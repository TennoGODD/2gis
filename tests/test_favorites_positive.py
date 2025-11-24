import allure
import requests
import pytest
import time
from config.base_test import BaseTest


@allure.epic("API 2GIS")
@allure.feature("Позитивные тесты избранных мест")
class TestFavoritesPositive(BaseTest):

    def setup_method(self):
        super().setup_method()

    @allure.title("01. Создание избранного места только с обязательными полями")
    @pytest.mark.order(1)
    def test_create_favorite_required_fields_only(self, fresh_token, favorite_payloads):
        favorite = self.favorites_api.create_favorite(
            token=fresh_token,
            **favorite_payloads["valid"]
        )

        assert favorite.id is not None, "ID не должен быть пустым"
        assert favorite.title == favorite_payloads["valid"]["title"]
        assert favorite.lat == favorite_payloads["valid"]["lat"]
        assert favorite.lon == favorite_payloads["valid"]["lon"]
        assert favorite.color is None, "Цвет должен быть None когда не указан"
        assert favorite.created_at is not None, "Дата создания не должна быть пустой"

    @allure.title("02. Создание избранного места со всеми полями включая цвет")
    @pytest.mark.order(2)
    def test_create_favorite_with_all_fields(self, fresh_token, favorite_payloads):
        favorite = self.favorites_api.create_favorite(
            token=fresh_token,
            **favorite_payloads["with_color"]
        )

        assert favorite.id is not None
        assert favorite.title == favorite_payloads["with_color"]["title"]
        assert favorite.color == "GREEN", "Цвет должен соответствовать указанному значению"

    @allure.title("03. Создание мест с разными цветами")
    @pytest.mark.parametrize("color", ["BLUE", "GREEN", "RED", "YELLOW"])
    @pytest.mark.order(3)
    def test_create_favorite_with_different_colors(self, fresh_token, color):
        favorite = self.favorites_api.create_favorite(
            title=f"Место с цветом {color}",
            lat=55.7558,
            lon=37.6176,
            color=color,
            token=fresh_token
        )

        assert favorite.color == color, f"Цвет должен быть {color}"

    @allure.title("04. Граничные значения для длины названия")
    @pytest.mark.parametrize("length,description", [
        (1, "минимальная длина"),
        (999, "максимальная длина")
    ])
    @pytest.mark.order(4)
    def test_create_favorite_title_boundary_length(self, fresh_token, length, description):
        title = "Т" * length
        favorite = self.favorites_api.create_favorite(
            title=title,
            lat=55.7558,
            lon=37.6176,
            token=fresh_token
        )

        assert favorite.title == title
        assert len(favorite.title) == length

    @allure.title("05. Разные допустимые символы в названии")
    @pytest.mark.parametrize("title", [
        "Test Place",  # латиница
        "Тестовое место",  # кириллица
        "Place 123",  # цифры
        "Place, with. punctuation!",  # знаки препинания
        "Место, 123!",  # комбинация
    ])
    @pytest.mark.order(5)
    def test_create_favorite_with_different_characters(self, fresh_token, title):
        favorite = self.favorites_api.create_favorite(
            title=title,
            lat=55.7558,
            lon=37.6176,
            token=fresh_token
        )

        assert favorite.title == title

    @allure.title("06. Разные допустимые координаты")
    @pytest.mark.parametrize("lat,lon,description", [
        (55.7558, 37.6176, "Москва"),
        (59.9343, 30.3351, "Санкт-Петербург"),
        (51.5074, -0.1278, "Лондон"),
        (40.7128, -74.0060, "Нью-Йорк"),
        (-33.8688, 151.2093, "Сидней"),
        (0.0, 0.0, "Нулевой остров"),
    ])
    @pytest.mark.order(6)
    def test_create_favorite_with_different_coordinates(self, fresh_token, lat, lon, description):
        response = requests.post(
            url="https://regions-test.2gis.com/v1/favorites",
            data={
                "title": f"Место в {description}",
                "lat": lat,
                "lon": lon
            },
            cookies={"token": fresh_token}
        )

        assert response.status_code == 200, (
            f"Ожидался статус 200 для координат ({lat}, {lon}), но получен {response.status_code}\n"
            f"Ответ: {response.text}"
        )

        favorite_data = response.json()
        favorite = self.favorites_api.create_favorite(
            title=f"Место в {description}",
            lat=lat,
            lon=lon,
            token=fresh_token
        )

        assert favorite.lat == lat
        assert favorite.lon == lon


