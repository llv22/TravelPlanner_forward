import os
import pickle
import json

# Define your input and output folders
pickle_folder = './evaluation/langfun_validation/sole-planning'
output_folder = './loaded_pickle/langfun_validation/by-day'

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Function to load a pickle file
def load_pickle(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)

# Function to save data as a JSON file
def save_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

# Process each pickle file
for filename in os.listdir(pickle_folder):
    if filename.endswith('.pkl'):
        pickle_path = os.path.join(pickle_folder, filename)
        
        # Define the output JSON file path
        json_filename = os.path.splitext(filename)[0] + '.json'
        json_path = os.path.join(output_folder, json_filename)
        
        try:
            # Try loading data and converting to JSON
            with open(pickle_path, 'rb') as f:
                data = pickle.load(f)
            
            # Stringify non-serializable objects before saving
            data_json = json.dumps(data, default=str, indent=4)
            
            with open(json_path, 'w') as f:
                json.dump(data_json, f, indent=4)
            
            print(f'Converted {pickle_path} to {json_path}')
        
        except Exception as e:
            print(f'Failed to convert {pickle_path} to JSON. Error: {str(e)}')