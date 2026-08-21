#!/usr/bin/env python

# This tool will list all the available files along with their file
# IDs currently stored on the OpenAI online storage.

import sys
from openai import OpenAI

client = OpenAI()

files = client.files.list()

print()
for f in files.data:
    print(f.id, f.filename, f.purpose)
print()