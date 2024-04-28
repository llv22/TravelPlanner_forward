import pickle
import json
import os

def load_pickle_file(index):
    file_path = f"./evaluation/langfun_validation/sole-planning/generated_plan_{index}.pkl"
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
            print(data)
    else:
        print(f"No pickle file found for index {index}")

def load_json_file_and_print_index(json_file_path, index):
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as f:
            data = json.load(f)
            if index < len(data):
                print(f"Data for index {index} from JSON file:")
                print(data[index - 1])
            else:
                print(f"No data found for index {index} in JSON file.")
    else:
        print(f"JSON file not found at path: {json_file_path}")

def main():
    index = 1  # Change this to the desired index
    load_pickle_file(index)

    json_file_path = "langfungpt4_data_record.json"  # Change this to the actual path
    load_json_file_and_print_index(json_file_path, index)

if __name__ == "__main__":
    main()