import pyglove as pg

@pg.members([
    ('mode', pg.typing.Str()),
    ('departure_city', pg.typing.Str()),
    ('arrival_city', pg.typing.Str())
])
class Transportation(pg.Object):
    pass

@pg.members([
    ('flight_number', pg.typing.Str()),
    ('departure_time', pg.typing.Str()),
    ('arrival_time', pg.typing.Str())
])
class Flight(Transportation):
    pass

class SelfDriving(Transportation):
    pass

class Taxi(Transportation):
    pass

class OtherTransportation(Transportation):
    pass

@pg.members([
    ('name', pg.typing.Str()),
    ('cuisine', pg.typing.Str()),
    ('city', pg.typing.Str())
])
class Meal(pg.Object):
    pass

@pg.members([
    ('name', pg.typing.Str()),
    ('city', pg.typing.Str())
])
class Attraction(pg.Object):
    pass

@pg.members([
    ('name', pg.typing.Str()),
    ('city', pg.typing.Str())
])
class Accomodation(pg.Object):
    pass

@pg.members([
    ('day', pg.typing.Int()),
    ('current_city', pg.typing.Str()),
    ('transportation', pg.typing.Union[
        Flight, Transportation, pg.typing.Str()
    ].noneable()),
    ('breakfast', pg.typing.Union[Meal, pg.typing.Str()].noneable()),
    ('attraction', pg.typing.Union[Attraction, pg.typing.Str()].noneable()),
    ('lunch', pg.typing.Union[Meal, pg.typing.Str()].noneable()),
    ('dinner', pg.typing.Union[Meal, pg.typing.Str()].noneable()),
    ('accommodation', pg.typing.Union[Accomodation, pg.typing.Str()].noneable())
])
class Day(pg.Object):
    pass

# class Day(pg.Object):
#     day: int 
#     current_city: str
#     transportation: Flight | SelfDriving | Taxi | OtherTransportation | str | None
#     breakfast: str | None
#     attraction: str | None
#     lunch: str | None
#     dinner: str | None
#     accommodation: str | None

# class TravelPlan(pg.Object):
#     def _on_init(self):
#         pass

#     days: list[Day]

#     def __init__(self, num_days):
#         self.days = [Day(day_number) for day_number in range(1, num_days + 1)]