from tqdm import tqdm
import json
import pickle
import pyglove as pg
import argparse
from datasets import load_dataset

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.travel_planner_class import Day, Flight, SelfDriving, Taxi, OtherTransportation

def replace_none_with_dash(dictionary):
    for key in dictionary:
        if dictionary[key] is None or dictionary[key] == "" or dictionary[key] == "None":
            dictionary[key] = "-"
    return dictionary

def format_current_city(current_city) -> str:
    if " to " in current_city and not current_city.startswith("from ") and not current_city.startswith("From "):
        current_city = "From " + current_city
    return current_city

def format_meal(meal) -> str:
    if isinstance(meal, str):
        return "-"
    return f"{meal.name}, {meal.city}"

def format_accommodation(accommodation) -> str:
    if isinstance(accommodation, str):
        return "-"
    return f"{accommodation.name}, {accommodation.city}"

def format_attraction(attraction) -> str:
    if isinstance(attraction, str):
        return "-"
    return f"{attraction.name}, {attraction.city}"

def format_transportation(day: Day) -> str:
    if isinstance(day.transportation, Flight):
        return f"Flight Number: {day.transportation.flight_number}, from {day.transportation.departure_city} to {day.transportation.arrival_city}, Departure Time: {day.transportation.departure_time}, Arrival Time: {day.transportation.arrival_time}"
    elif isinstance(day.transportation, (SelfDriving, Taxi, OtherTransportation)):
        return f"{day.transportation.mode} from {day.transportation.departure_city} to {day.transportation.arrival_city}"
    elif isinstance(day.transportation, str):
        return day.transportation
    else:
        return "-"

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--set_type", type=str, default="validation")
    parser.add_argument("--model_name", type=str, default="gpt-3.5-turbo-1106")
    parser.add_argument("--mode", type=str, default="two-stage")
    parser.add_argument("--strategy", type=str, default="direct")
    parser.add_argument("--output_dir", type=str, default="./")
    parser.add_argument("--submission_file_dir", type=str, default="./")

    args = parser.parse_args()

    if args.mode == 'two-stage':
        suffix = ''
    elif args.mode == 'sole-planning':
        suffix = f'_{args.strategy}'

    if args.set_type == 'validation':
        query_data_list  = load_dataset('osunlp/TravelPlanner','validation')['validation']
    elif args.set_type == 'test':
        query_data_list  = load_dataset('osunlp/TravelPlanner','test')['test']

    idx_number_list = [i for i in range(1,len(query_data_list)+1)]

    submission_list = []

    for idx in tqdm(idx_number_list):
        if(args.model_name=="langfun"):
            with open(f'{args.output_dir}/{args.model_name}_{args.set_type}/{args.mode}/generated_plan_{idx}.pkl', 'rb') as f:
                plan = pickle.load(f)
                for day in range(len(plan)):
                    formatted_current_city = format_current_city(plan[day].current_city)
                    formatted_transportation = format_transportation(plan[day])
                    formatted_breakfast = format_meal(plan[day].breakfast) if plan[day].breakfast is not None else None
                    formatted_lunch = format_meal(plan[day].lunch) if plan[day].lunch is not None else None
                    formatted_dinner = format_meal(plan[day].dinner) if plan[day].dinner is not None else None
                    formatted_accommodation = format_accommodation(plan[day].accommodation) if plan[day].accommodation is not None else None
                    formatted_attraction = format_attraction(plan[day].attraction) if plan[day].attraction is not None else None
                    pg.patching.patch_on_key(plan[day], 'current_city', formatted_current_city)
                    pg.patching.patch_on_key(plan[day], 'transportation', formatted_transportation)
                    pg.patching.patch_on_key(plan[day], 'breakfast', formatted_breakfast)
                    pg.patching.patch_on_key(plan[day], 'lunch', formatted_lunch)
                    pg.patching.patch_on_key(plan[day], 'dinner', formatted_dinner)
                    pg.patching.patch_on_key(plan[day], 'attraction', formatted_attraction)
                    pg.patching.patch_on_key(plan[day], 'accommodation', formatted_accommodation)
                    plan[day] = plan[day].__dict__["_sym_attributes"]
                    plan[day] = replace_none_with_dash(plan[day])
        else:
            generated_plan = json.load(open(f'{args.output_dir}/{args.model_name}_{args.set_type}/{args.mode}/generated_plan_{idx}.json'))
            #print(generated_plan)
            try:
                plan = generated_plan[-1][f'{args.model_name}{suffix}_{args.mode}_parsed_results']
            except:
                plan = None
        submission_list.append({"idx":idx,"query":query_data_list[idx - 1]['query'],"plan":plan})
    with open(f'{args.submission_file_dir}/{args.set_type}_{args.model_name}{suffix}_{args.mode}_submission.jsonl','w',encoding='utf-8') as w:
        for unit in submission_list:
            output = json.dumps(unit)
            w.write(output + "\n")
        w.close()
