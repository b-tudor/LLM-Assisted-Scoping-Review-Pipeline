#!/usr/bin/env python

# This tool cancels all batches that are currently running/submitted 


from openai import OpenAI

client = OpenAI()

# Define terminal states where batches no longer count toward token quota
TERMINAL_STATES = {"completed", "failed", "cancelled", "expired"}

def cancel_all_batches():
    cancelled = []
    still_active = []

    # List batches (SDK paginates automatically if needed)
    batches = client.batches.list(limit=100)

    for batch in batches:
        if batch.status not in TERMINAL_STATES:
            print(f"Cancelling batch {batch.id} (status={batch.status}) ...")
            try:
                client.batches.cancel(batch.id)
            except:
                print(f"Cancellation failed (Job not running?)")
            cancelled.append(batch.id)
        else:
            still_active.append((batch.id, batch.status))

    print("\n=== Summary ===")
    print(f"Cancelled {len(cancelled)} batches: {cancelled}")
    print(f"Left {len(still_active)} already terminal batches: {still_active}")

if __name__ == "__main__":
    cancel_all_batches()