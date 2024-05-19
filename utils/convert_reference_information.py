import json
import ast

def parse_array_string(array_string):
    # Split the string into individual items
    items = ast.literal_eval(array_string)
    output = ""
    for item in items:
        # Split each item into key-value pairs
        # if item[0] == '[':
        #     item = item[1:]
        # if item[-1] == ']':
        #     item = item[:-1]
        # if(item[0] != '{'):
        #     item = '{' + item
        # if(item[-1] != '}'):
        #     item = item + '}'

        print("item: ", item)

        description = item['Description']
        content = item['Content']

        output += f"Description: {description}\n```csv\n{content}\n```\n"
    
    return output

# Example usage
array_string = open('reference.txt', 'r').read()
output_string = parse_array_string(array_string)
open('output.txt', 'w').write(output_string)