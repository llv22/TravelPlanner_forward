import json
import pickle
import pyglove as pg
import sys

def load_line_json_data(filename):
    data = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f.read().strip().split('\n'):
            unit = json.loads(line)
            data.append(unit)
    return data

class ModifiedDay(pg.Object):
    day: int | None
    current_city: str | None
    transportation: str | None
    breakfast: str | None
    attraction: str | None
    lunch: str | None
    dinner: str | None
    accommodation: str | None

    @pg.explicit_method_override
    def __init__(self, data):
        super().__init__()
        self.day = data.day
        self.current_city = data.current_city
        self.transportation = str(data.transportation)
        self.breakfast = data.breakfast
        self.attraction = data.attraction
        self.lunch = data.lunch
        self.dinner = data.dinner
        self.accommodation = data.accommodation

if(__name__ == '__main__'):
    # Parse the loaded string into a Python object
    # loaded_object = json.loads(open("test.json").read())
    # element = loaded_object
    with open('generated_plan_1 copy.pkl', 'rb') as f:
        loaded_data = pickle.load(f)
    print(loaded_data[0], loaded_data[1], loaded_data[2])
    #unit = loaded_data[0]
    #print(unit)
    #pg.patching.patch_on_key(unit, 'transportation', "lmfaoo finally")
    #print(unit.__dict__["_sym_attributes"])
    # modified_day = ModifiedDay(loaded_data[0]
    # print(modified_day)