#!/usr/bin/env python3
import sys
import json

argc = len(sys.argv)
if (argc != 2):
    print(f"Usage:\n\t{sys.argv[0]} <jsonl-file>")
    print(f'CSV data is output to terminal. Redirect output to a CSV file.\nE.g.:')
    print(f'\t{sys.argv[0]} input_file.jsonl > output_file.csv')
    exit(1)

file_path = sys.argv[1]


#print(f'id,include,confidence,reasoning')
with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        # Strip whitespace/newlines
        line = line.strip()
        if not line:
            continue  # skip empty lines
        # Parse the JSON object
        obj = json.loads(line)
        
        # Do something with the object
        id = int(obj["custom_id"][-4:])
        print(f'{id},{obj["response"]["body"]["output"][1]["content"][0]["text"]}')
