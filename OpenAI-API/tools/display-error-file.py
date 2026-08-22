#!/usr/bin/env python
import sys
from openai import OpenAI

argc = len(sys.argv)
if (argc != 2):
	print(f"Usage:\n\t{sys.argv[0]} <error_file_id>")
	if argc > 2:
		print(f'NOTE: File IDs should start with "file-"')
	exit(0)
fileID = sys.argv[1]

client = OpenAI()

err_id = fileID
if err_id:
    stream = client.files.content(err_id)
    with open("batch_errors.jsonl", "wb") as f:
        f.write(stream.read())

# Peek at a few lines
with open("batch_errors.jsonl", "r") as f:
    for i, line in enumerate(f):
        if i == 10: break
        print(line.strip())
