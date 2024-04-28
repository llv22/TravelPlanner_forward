import pyglove as pg

class Transportation(pg.Object):
    mode: str

class Flight(Transportation):
    flight_number: str
    departure_time: str
    arrival_time: str

class OtherTransportation(Transportation):
    pass

class Day(pg.Object):
    day: int 
    current_city: str
    transportation: Flight | OtherTransportation | None
    breakfast: str | None
    attraction: str | None
    lunch: str | None
    dinner: str | None
    accommodation: str | None

# class TravelPlan(pg.Object):
#     def _on_init(self):
#         pass

#     days: list[Day]

#     def __init__(self, num_days):
#         self.days = [Day(day_number) for day_number in range(1, num_days + 1)]