import csv
import json


# Function to calculate the percentage of success
def calculate_percentage(true_count, total_count):
    return (true_count / total_count) if total_count != 0 else 0


# Read data from the JSON file
with open("evaluated_scores.json", "r") as file:
    data = json.load(file)

csv_data = []

# Traverse the data dictionary and calculate percentages
for constraint_type, difficulties in data.items():
    for difficulty, levels in difficulties.items():
        for level, constraints in levels.items():
            for constraint, values in constraints.items():
                true_count = values.get("true", 0)
                false_count = values.get("false", 0)
                total_count = values.get("total", 0)
                percentage = calculate_percentage(true_count, total_count)
                csv_data.append(
                    [
                        constraint_type,
                        difficulty,
                        level,
                        constraint,
                        true_count,
                        false_count,
                        total_count,
                        percentage,
                    ]
                )

# Write to CSV
with open("constraints.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(
        [
            "Category",
            "Difficulty",
            "Level",
            "Constraint",
            "'True",
            "'False",
            "Total",
            "Success Percentage",
        ]
    )
    writer.writerows(csv_data)

print("CSV file created successfully.")
