#!/usr/bin/env python3

import sys
import json

if len(sys.argv) != 2:
    print(f'Usage:\n\t{sys.argv[0]} <input_file>')
    print(f'CSV data is output to terminal. Redirect output to a CSV file.\nE.g.:')
    print(f'\t{sys.argv[0]} input_file.jsonl > output_file.csv')
    exit(1)

INPUT_FILE = sys.argv[1]


with open(INPUT_FILE, "r", encoding="utf-8") as infile:
    print('id,decision,confidence,reason')
    for line in infile:
        if not line.strip():
            continue
        
        obj = json.loads(line)
        
        # Extract custom_id (strip leading zeros if numeric)
        id = int(obj.get("custom_id", ""))
        
        print(f'{id},{obj["response"]["output"][1]["content"][0]["text"]}')
        continue
        
