#!/usr/bin/env python

# This tool checks thet status of the batch specified by number on the command line.


import sys
from openai import OpenAI
client = OpenAI()

argc = len(sys.argv)
if (argc != 2):
	print(f"Usage:\n\t{sys.argv[0]} <batch_id>")
	if argc > 2:
		print(f'NOTE: Batch IDs should start with "batch_"')
	exit(0)
batchID = sys.argv[1]


batch = client.batches.retrieve(batchID)
print(batch)
print()
print(f'      Batch ID: {batch.id}')
print(f'          File: {batch.input_file_id}')
print(f'        Errors: {batch.errors}')
print(f'        Status: {batch.status}')
print(f'Output File ID: {batch.output_file_id}')
print()
