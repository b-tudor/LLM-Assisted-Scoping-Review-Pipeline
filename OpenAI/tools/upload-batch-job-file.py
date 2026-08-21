#!/usr/bin/env python3
import sys
from openai import OpenAI

argc = len(sys.argv)
if (argc != 2):
	print(f"Usage:\n\t{sys.argv[0]} <input_file>")
	if argc > 2:
		print(f'NOTE: Only a single file is allowed to be uploaded at a time (for now).')
	exit(0)
filename = sys.argv[1]

filename_parts = filename.split('.')
filename_partcount = len(filename_parts)
if (filename_partcount==1) or (filename_parts[filename_partcount-1] != "jsonl"):
	print("File type should be .jsonl\nExiting...")
	exit(0)

print(f'Batch file name: {filename}')


client = OpenAI()

batch_input_file = client.files.create(
    file=open(filename, "rb"),
    purpose="batch"
)

print(batch_input_file)
print()
print( f'Batch File ID: {batch_input_file.id}')
print( f'         Name: {batch_input_file.filename}')
print( f'         Size: {batch_input_file.bytes}')
print( f'      Purpose: {batch_input_file.purpose}')
print( f' status_deets: {batch_input_file.status_details}')
