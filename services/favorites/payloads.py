class Payloads:
    @staticmethod
    def create_favorite(title: str, lat: float, lon: float, color: str = None):
        payload = {
            "title": title,
            "lat": lat,
            "lon": lon
        }
        if color:
            payload["color"] = color
        return payload