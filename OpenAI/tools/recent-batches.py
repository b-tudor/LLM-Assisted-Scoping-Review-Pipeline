#!/usr/bin/env python3
import sys
from openai import OpenAI


client = OpenAI()

batches = client.batches.list()

for b in batches.data:
    print(b.id, b.status, b.request_counts.total, b.metadata)
    