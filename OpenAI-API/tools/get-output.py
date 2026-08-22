#!/usr/bin/env python

# This tool will download a single batch output file,
# given the batch id number (specified from the command line)

import sys
from openai import OpenAI


argc = len(sys.argv)
if (argc != 3):
	print(f"Usage:\n\t{sys.argv[0]} <batch_id> <output_file>")
	print(f'NOTE: Batch IDs should start with "batch_"')
	if argc > 3:
		print(f'NOTE: This script only supports fetching one output stream at a time. Sorry.')
	exit(0)
batchID = sys.argv[1]
outFile = sys.argv[2]

client = OpenAI()

b = client.batches.retrieve(batchID)

print(b.status, b.request_counts)
print("output_file_id:", b.output_file_id)

# Download the output file
stream = client.files.content(b.output_file_id)
with open(outFile, "wb") as f:
    f.write(stream.read())

print(f'output saved as "{outFile}"')
