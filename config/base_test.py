from services.auth.api_auth import AuthAPI
from services.favorites.api_favorites import FavoritesAPI


class BaseTest:

    def setup_method(self):
        self.auth_api = AuthAPI()
        self.favorites_api = FavoritesAPI()