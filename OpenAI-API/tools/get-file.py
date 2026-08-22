#!/usr/bin/env python

# This will download a single file (specified by the file ID from the command line)

import sys
from openai import OpenAI

job_desc = "test job"

argc = len(sys.argv)
if (argc != 2):
	print(f"Usage:\n\t{sys.argv[0]} <file_id>")
	if argc > 2:
		print(f'NOTE: This only supports fetching one file at a time. Sorry.')
	print(f'NOTE: File IDs should start with "file-"')
	exit(0)
fileID = sys.argv[1]

client = OpenAI()

# Get file contents
stream = client.files.content(fileID)

# Save to disk
with open("output.jsonl", "wb") as f:
    f.write(stream.read())

print("File saved as output.jsonl")
