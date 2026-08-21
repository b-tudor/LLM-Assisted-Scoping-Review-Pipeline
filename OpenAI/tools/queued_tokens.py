#!/usr/bin/env python

# This tool will list how many enqueued tokens the system thinks
# are currently awaiting processing. 

from openai import OpenAI

client = OpenAI()

TERMINAL = {"completed", "failed", "cancelled", "expired"}

def check_enqueued_tokens():
    total_enqueued = 0
    active_batches = []

    for batch in client.batches.list():
        # Some SDKs return `request_counts` instead of token counts directly
        count_info = getattr(batch, "request_counts", None)
        tokens = 0

        if count_info:
            tokens = getattr(count_info, "total", 0)

        if batch.status not in TERMINAL:
            total_enqueued += tokens
            active_batches.append((batch.id, batch.status, tokens))

    print("=== Batch Token Monitor ===")
    print(f"Total enqueued tokens (non-terminal batches): {total_enqueued}")
    if active_batches:
        for b in active_batches:
            print(f" - {b[0]} (status={b[1]}, tokens={b[2]})")
    else:
        print("No active batches — all jobs are in terminal states.")

if __name__ == "__main__":
    check_enqueued_tokens()