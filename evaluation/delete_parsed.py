import os
import json

# Specify the folder containing the JSON files
folder_path = 'gpt-4-1106-preview_validation/sole-planning'

# Iterate through each file in the folder
for filename in os.listdir(folder_path):
    # Check if the file is a JSON file
    if filename.endswith('.json'):
        file_path = os.path.join(folder_path, filename)
        
        # Load the JSON content
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Check if the unwanted key exists and delete it
        if 'gpt-4-1106-preview_direct_sole-planning_parsed_results' in data[0]:
            del data[0]['gpt-4-1106-preview_direct_sole-planning_parsed_results']
        
        # Save the modified JSON content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

print("Processing complete. The specified keys have been removed from all JSON files.")
