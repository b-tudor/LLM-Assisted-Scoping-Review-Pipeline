#!/usr/bin/env python

# This tool creates a batch job from a file that has been uploaded onto the OpenAI storage.

import sys
from openai import OpenAI

job_desc = "Screen X.X.n: Full text screening of articles selected in screen."

argc = len(sys.argv)
if (argc != 2):
	print(f"Usage:\n\t{sys.argv[0]} <file_id>")
	if argc > 2:
		print(f'NOTE: This script only supports 1 batch job submission at a time. Ty for your understanding.')
	print(f'NOTE: File IDs should start with "file-"')
	exit(0)
fileID = sys.argv[1]

client = OpenAI()

batch_input_file_id = fileID
batch = client.batches.create(
    input_file_id=batch_input_file_id,
    endpoint="/v1/responses",
    completion_window="24h",
    metadata={
        "description": job_desc
    }
)

print(f'Batch ID: {batch.id}')
