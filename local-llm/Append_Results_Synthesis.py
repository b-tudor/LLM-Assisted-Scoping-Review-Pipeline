import os
import csv
import re

# Paths
input_dir = "/analysis_results_Synthesis"
output_dir = "/Final_Output"
output_file = os.path.join(output_dir, "combined_output.csv")

MARKER = "--- Chunk 1 ---"

# Make sure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Collect .txt files (sorted for reproducibility)
txt_files = sorted(f for f in os.listdir(input_dir) if f.lower().endswith(".txt"))

def extract_after_marker(text: str, marker: str) -> str:
    """Return everything after the first occurrence of `marker`."""
    idx = text.find(marker)
    if idx == -1:
        return ""
    return text[idx + len(marker):].strip()

def extract_numeric(filename: str) -> str:
    """Extract only the numeric part of a filename."""
    match = re.findall(r"\d+", filename)
    return match[0] if match else filename

# Write CSV
with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)

    for filename in txt_files:
        path = os.path.join(input_dir, filename)
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()

        content = extract_after_marker(raw, MARKER)
        file_id = extract_numeric(filename)

        # Extract items inside double quotes
        fields = re.findall(r'"([^"]+)"', content)

        # Prepend the file ID
        row = [file_id] + fields
        writer.writerow(row)

print(f"✅ CSV created at: {output_file}")
