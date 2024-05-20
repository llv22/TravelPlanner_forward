import json
import pickle
import pyglove as pg
import sys

if(__name__ == '__main__'):
    with open('./evaluation/langfun_validation/sole-planning/generated_plan_1.pkl', 'rb') as f:
        loaded_data = pickle.load(f)
    print(loaded_data[0], loaded_data[1], loaded_data[2])