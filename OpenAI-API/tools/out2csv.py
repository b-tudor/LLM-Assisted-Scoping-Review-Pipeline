#!/usr/bin/env python

# This tool will take one of the title/abstract screening output
# files and convert it to csv format.


import sys
import json

argc = len(sys.argv)
if (argc != 2):
	print(f"Usage:\n\t{sys.argv[0]} <jsonl-file>")
	exit(0)
file_path = sys.argv[1]


print(f'id,include,confidence,reasoning')
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
        print(f'{id}, {obj["response"]["body"]["output"][1]["content"][0]["text"]}')
