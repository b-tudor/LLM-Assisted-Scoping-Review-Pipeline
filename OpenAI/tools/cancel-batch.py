#!/usr/bin/env python

# This tool cancels the batch specified by number on the command line


import sys
from openai import OpenAI

job_desc = "test job"

argc = len(sys.argv)
if (argc != 2):
	print(f"Usage:\n\t{sys.argv[0]} <batch_id>")
	if argc > 2:
		print(f'NOTE: Batch IDs should start with "batch_"')
	exit(0)
batchID = sys.argv[1]

client = OpenAI()

client.batches.cancel(batchID)