class Headers:
    @staticmethod
    def with_token(token: str):
        return {"Cookie": f"token={token}"}