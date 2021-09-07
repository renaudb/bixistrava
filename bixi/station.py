class Station(object):
    """Bixi station data class."""
    def __init__(self, id: str, name: str, lat: float, lng: float):
        self.id = id
        self.name = name
        self.lat = lat
        self.lng = lng

    def __repr__(self) -> str:
        return f'Station([{self.id}, {self.name}, {self.lat}, {self.lng}])'
