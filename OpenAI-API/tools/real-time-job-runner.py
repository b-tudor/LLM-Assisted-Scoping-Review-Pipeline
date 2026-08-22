#!/usr/bin/env python3

# This tool takes a jsonl file of requests and submits them one at a time to the 
# real-time OpenAI API (as opposed to the batch method). It will retry upon failure
# and it will pause slightly between submission in order to try and not exceed the
# max token/minute rate.

import sys
import json
import time
from openai import OpenAI
from pathlib import Path


client = OpenAI()

SLEEP_SECONDS = 2.0     # adjust if you hit rate limits
MAX_RETRIES = 3

def process_line(line_obj):
    """
    Takes a dict (parsed JSON line) and sends it to the Responses API.
    Expects 'body' key with model + input, similar to your batch file.
    """
    body = line_obj.get("body", {})
    try:
        resp = client.responses.create(**body)
        return {
            "custom_id": line_obj.get("custom_id"),
            "status": "success",
            "response": resp.model_dump()
        }
    except Exception as e:
        return {
            "custom_id": line_obj.get("custom_id"),
            "status": "error",
            "error": str(e)
        }




if len(sys.argv) != 3:
    print(f'Usage:\n\t{sys.argv[0]} <input_file> <output_file>\n<input_file> should be of type JSONL.\nOutput is appended to <output_file> with JSONL formatting.')
    exit(1)

INPUT_FILE  = sys.argv[1]
OUTPUT_FILE = sys.argv[2]

print(f' Input file: {INPUT_FILE}' )
print(f'Output file: {OUTPUT_FILE}')

input_path  = Path( INPUT_FILE)
output_path = Path(OUTPUT_FILE)

with input_path.open("r", encoding="utf-8") as infile, \
        output_path.open("a", encoding="utf-8") as outfile:

    for line in infile:
        if not line.strip():
            continue

        obj = json.loads(line)
        print(f"Processing ID {obj.get('custom_id')}")
        retries = 0
        result = None

        while retries < MAX_RETRIES:
            result = process_line(obj)
            if result["status"] == "success":
                break
            else:
                retries += 1
                print(f"Retry {retries}/{MAX_RETRIES} for {obj.get('custom_id')}")
                time.sleep(SLEEP_SECONDS * retries * 2.5 )  # wait a bit longer before retry

        if result is None or result["status"] == "error":
            print(f"Skipping {obj.get('custom_id')} after {MAX_RETRIES} retries")

        # Write the result (success or error) to output.jsonl
        outfile.write(json.dumps(result) + "\n")
        outfile.flush()

        # Sleep to respect rate limits
        time.sleep(SLEEP_SECONDS)


