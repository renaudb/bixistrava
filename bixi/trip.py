from datetime import datetime, timedelta

from bixi.station import Station


class Trip(object):
    """Bixi trip data class."""
    def __init__(self, start_dt: datetime, start_station: Station,
                 end_dt: datetime, end_station: Station):
        self.start_dt = start_dt
        self.start_station = start_station
        self.end_dt = end_dt
        self.end_station = end_station

    @property
    def duration(self) -> timedelta:
        """Returns trip duration."""
        return self.end_dt - self.start_dt

    def __repr__(self) -> str:
        return f'Trip([{self.start_dt}, {self.start_station}, {self.end_dt}, {self.end_station}])'
