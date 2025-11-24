import allure
import pytest
import time
from datetime import datetime, timezone
from config.base_test import BaseTest


@allure.epic("API 2GIS")
@allure.feature("Функциональные тесты избранных мест")
class TestFavoritesFunctional(BaseTest):

    def setup_method(self):
        super().setup_method()

    @allure.title("01. Проверка точности времени сервера")
    @pytest.mark.order(1)
    def test_server_time_accuracy(self, fresh_token):
        time_differences = []
        max_allowed_difference = 300

        for i in range(3):
            time_before_utc = datetime.now(timezone.utc)

            favorite = self.favorites_api.create_favorite(
                title=f"Проверка времени {i + 1}",
                lat=55.7558 + i * 0.001,
                lon=37.6176 + i * 0.001,
                token=fresh_token
            )

            time_after_utc = datetime.now(timezone.utc)

            server_time_str = favorite.created_at
            server_time = datetime.fromisoformat(server_time_str.replace('Z', '+00:00'))
            server_time_utc = server_time.astimezone(timezone.utc)

            avg_real_time_utc = time_before_utc + (time_after_utc - time_before_utc) / 2
            time_difference = (server_time_utc - avg_real_time_utc).total_seconds()
            time_differences.append(time_difference)

            import time
            if i < 2:
                time.sleep(0.5)

        avg_difference = sum(time_differences) / len(time_differences)
        max_deviation = max(abs(diff) for diff in time_differences)
        all_within_tolerance = all(abs(diff) <= max_allowed_difference for diff in time_differences)

        allure.attach(
            f"РЕЗУЛЬТАТЫ 3 ПРОВЕРОК ВРЕМЕНИ:\n"
            f"Проверка 1: {time_differences[0]:+.1f} секунд\n"
            f"Проверка 2: {time_differences[1]:+.1f} секунд\n"
            f"Проверка 3: {time_differences[2]:+.1f} секунд\n"
            f"МАКСИМАЛЬНОЕ ОТКЛОНЕНИЕ: {max_deviation:.1f} секунд\n"
            f"СТАТУС: {'ПРОЙДЕНО' if all_within_tolerance else 'НЕ ПРОЙДЕНО'}",
            name="Анализ точности времени сервера"
        )

        if not all_within_tolerance:
            failed_checks = []
            for i, diff in enumerate(time_differences):
                if abs(diff) > max_allowed_difference:
                    direction = "впереди" if diff > 0 else "позади"
                    failed_checks.append(f"Проверка {i + 1}: {abs(diff):.1f}сек {direction}")

            pytest.fail(
                f"ОШИБКА ТОЧНОСТИ ВРЕМЕНИ СЕРВЕРА\n"
                f"Время сервера не синхронизировано с UTC в допустимых пределах.\n\n"
                f"Не пройденные проверки ({len(failed_checks)}/3):\n" + "\n".join(failed_checks) + f"\n\n"
                f"Максимальное отклонение: {max_deviation:.1f} секунд\n"
            )
        else:
            direction = "впереди" if avg_difference > 0 else "позади"
            allure.dynamic.title(f"07. Проверка точности времени сервера - ПРОЙДЕНО ({avg_difference:+.1f}сек {direction})")

    @allure.title("02. Проверка уникальности ID")
    @pytest.mark.order(2)
    def test_id_uniqueness_and_monotonic_increase(self, fresh_token):
        favorites = []

        for i in range(3):
            favorite = self.favorites_api.create_favorite(
                title=f"Тестовое место {i}",
                lat=55.7558 + i * 0.001,
                lon=37.6176 + i * 0.001,
                token=fresh_token
            )
            favorites.append(favorite)

        ids = [f.id for f in favorites]
        assert len(ids) == len(set(ids)), "Все ID должны быть уникальными"

    @allure.title("03. Проверка точности координат")
    @pytest.mark.order(3)
    def test_coordinate_precision(self, fresh_token):
        precise_lat = 55.123456789
        precise_lon = 37.987654321

        favorite = self.favorites_api.create_favorite(
            title="Место с точными координатами",
            lat=precise_lat,
            lon=precise_lon,
            token=fresh_token
        )

        assert favorite.lat == precise_lat, f"Ожидалось {precise_lat}, получено {favorite.lat}"
        assert favorite.lon == precise_lon, f"Ожидалось {precise_lon}, получено {favorite.lon}"

    @allure.title("04. Проверка монотонного возрастания ID")
    @pytest.mark.order(4)
    def test_id_monotonic_increase(self, fresh_token):
        favorites = []

        for i in range(3):
            favorite = self.favorites_api.create_favorite(
                title=f"Место для проверки ID {i}",
                lat=55.7558 + i * 0.01,
                lon=37.6176 + i * 0.01,
                token=fresh_token
            )
            favorites.append(favorite)
            time.sleep(0.1)

        ids = [f.id for f in favorites]

        for i in range(1, len(ids)):
            assert ids[i] > ids[i - 1], f"ID не увеличиваются монотонно: {ids[i - 1]} -> {ids[i]}"

        allure.attach(f"ID последовательность: {ids}", name="ID Sequence")