#!/usr/bin/env python

# This tool deletes a file from OpenAI online storage (specified by file ID on the command line)

import sys
from openai import OpenAI

job_desc = "test job"



argc = len(sys.argv)
if (argc != 2):
	print(f"Usage:\n\t{sys.argv[0]} <file_id>")
	if argc > 2:
		print(f'NOTE: This only supports deleteing one file at a time. Sorry.')
	print(f'NOTE: File IDs should start with "file-"')
	exit(0)
fileID = sys.argv[1]

client = OpenAI()

client.files.delete(fileID)
print(f"Deleted {fileID}")
