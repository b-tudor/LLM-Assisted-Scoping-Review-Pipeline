#!/usr/bin/env python3
"""
LM Studio batch analyzer with chunking for ~20k token models.
- Reads ONLY whitelisted .txt files from BASE_DIR
- Splits files larger than MAX_CHARS_PER_CALL into smaller chunks
- Saves <filename>.analysis.txt in OUTPUT_DIR
- Collects Y/N,confidence,rationale from ALL chunks into OUTPUT_DIR/decisions.csv
"""

import os
import sys
import time
import csv
import re
from pathlib import Path

try:
    from openai import OpenAI
except Exception:
    print("ERROR: pip install openai>=1.0.0 required.")
    sys.exit(1)

# ======= CONFIGURATION =======
BASE_DIR = Path("./outputs")
OUTPUT_DIR = Path("./analysis_results")
BASE_URL = "http://127.0.0.1:1234/v1"
MODEL_NAME = "openai/gpt-oss-20b"
MAX_CHARS_PER_CALL = 190000  # safe for ~45k tokens
RETRIES = 3
# =============================

DECISIONS_CSV = OUTPUT_DIR / "decisions.csv"

# ======= ALLOWED FILES LIST =======
ALLOWED_FILES = {
     "1.txt", "10.txt", "100.txt", "1002.txt", "1006.txt", "1012.txt", "1019.txt",
    "1025.txt", "103.txt", "1032.txt", "1043.txt", "1055.txt", "1059.txt",
    "1067.txt", "1069.txt", "1073.txt", "1079.txt", "108.txt", "1085.txt",
    "11.txt", "1105.txt", "1111.txt", "1117.txt", "1118.txt", "1119.txt",
    "1122.txt", "1128.txt", "1130.txt", "1134.txt", "1140.txt", "1146.txt",
    "1149.txt", "1152.txt", "1157.txt", "1159.txt", "1162.txt", "1165.txt",
    "1166.txt", "1168.txt", "1170.txt", "1171.txt", "1172.txt", "1173.txt",
    "118.txt", "1192.txt", "1193.txt", "1200.txt", "1202.txt", "1215.txt",
    "1227.txt", "1235.txt", "1257.txt", "1259.txt", "1260.txt", "1262.txt",
    "1263.txt", "1271.txt", "1279.txt", "128.txt", "129.txt", "1299.txt",
    "1303.txt", "131.txt", "1314.txt", "1316.txt", "135.txt", "137.txt",
    "148.txt", "149.txt", "157.txt", "167.txt", "19.txt", "190.txt", "195.txt",
    "210.txt", "211.txt", "217.txt", "232.txt", "236.txt", "242.txt", "244.txt",
    "245.txt", "260.txt", "264.txt", "274.txt", "289.txt", "29.txt", "295.txt",
    "30.txt", "300.txt", "304.txt", "312.txt", "315.txt", "321.txt", "322.txt",
    "324.txt", "333.txt", "334.txt", "337.txt", "343.txt", "346.txt", "347.txt",
    "352.txt", "354.txt", "364.txt", "367.txt", "386.txt", "389.txt", "39.txt",
    "394.txt", "397.txt", "399.txt", "402.txt", "407.txt", "414.txt", "416.txt",
    "417.txt", "436.txt", "439.txt", "442.txt", "456.txt", "462.txt", "466.txt",
    "47.txt", "476.txt", "481.txt", "485.txt", "49.txt", "498.txt", "500.txt",
    "503.txt", "507.txt", "51.txt", "514.txt", "522.txt", "524.txt", "525.txt",
    "533.txt", "545.txt", "554.txt", "570.txt", "593.txt", "595.txt", "597.txt",
    "612.txt", "628.txt", "63.txt", "631.txt", "632.txt", "635.txt", "64.txt",
    "654.txt", "66.txt", "662.txt", "668.txt", "678.txt", "682.txt", "687.txt",
    "70.txt", "700.txt", "715.txt", "72.txt", "73.txt", "739.txt", "743.txt",
    "755.txt", "756.txt", "76.txt", "764.txt", "767.txt", "770.txt", "774.txt",
    "779.txt", "781.txt", "784.txt", "791.txt", "799.txt", "80.txt", "809.txt",
    "81.txt", "811.txt", "812.txt", "815.txt", "821.txt", "822.txt", "826.txt",
    "833.txt", "836.txt", "841.txt", "846.txt", "848.txt", "85.txt", "851.txt",
    "854.txt", "858.txt", "859.txt", "867.txt", "880.txt", "885.txt", "889.txt",
    "895.txt", "898.txt", "9.txt", "901.txt", "909.txt", "912.txt", "917.txt",
    "921.txt", "922.txt", "937.txt", "941.txt", "946.txt", "948.txt", "949.txt",
    "957.txt", "958.txt", "965.txt", "966.txt", "973.txt", "975.txt", "977.txt",
    "996.txt"
}
# ==================================

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def iter_chunks(text: str, size: int):
    """Yield fixed-size character chunks from text."""
    for i in range(0, len(text), size):
        yield text[i:i+size]

def call_model(client: OpenAI, model: str, user_prompt: str) -> str:
    """Send a single prompt to the model and return output."""
    for attempt in range(1, RETRIES + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.2,
            )
            content = getattr(resp.choices[0].message, "content", "") or ""
            return content.strip()
        except Exception as e:
            print(f"Error on attempt {attempt}: {e}")
            if attempt == RETRIES:
                raise
            time.sleep(1.5 * attempt)
    return ""

def write_analysis_txt(src_path: Path, all_outputs: list[str]):
    """Save all chunk outputs into one .analysis.txt file."""
    out_path = OUTPUT_DIR / f"{src_path.stem}.analysis.txt"
    content = [f"# Analysis for: {src_path.name}", ""]
    for idx, chunk in enumerate(all_outputs, start=1):
        content.append(f"--- Chunk {idx} ---")
        content.append(chunk)
        content.append("")
    out_path.write_text("\n".join(content), encoding="utf-8")
    return out_path

def extract_all_decisions(raw: str):
    """
    Extract all 'Y/N,confidence,rationale' lines from output text.
    Returns a list of tuples (decision, confidence, rationale).
    """
    csv_pat = re.compile(r'^\s*([YyNn])\s*,\s*([\w\.\%]+)\s*,\s*(".*"|.+)\s*$', re.MULTILINE)
    matches = csv_pat.findall(raw)
    results = []
    for d, c, r in matches:
        d = d.upper()
        if len(r) >= 2 and r[0] == '"' and r[-1] == '"':
            r = r[1:-1]
        results.append((d, c.strip(), r.strip()))
    return results

def append_decision_rows(csv_path: Path, filename: str, chunk_num: int, decisions: list[tuple]):
    """Append all decisions from a chunk to the CSV file."""
    exists = csv_path.exists()
    with csv_path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["file", "chunk", "decision", "confidence", "rationale"])
        for d, c, r in decisions:
            writer.writerow([filename, chunk_num, d or "", c or "", r or ""])

def main():
    ensure_dir(OUTPUT_DIR)
    client = OpenAI(base_url=BASE_URL, api_key=os.environ.get("OPENAI_API_KEY", "not-needed"))

    # Gather only whitelisted text files
    txt_files = sorted(
        [f for f in BASE_DIR.glob("*.txt") if f.name in ALLOWED_FILES]
    )

    if not txt_files:
        print(f"No whitelisted .txt files found in {BASE_DIR}")
        return

    # Warn if expected files are missing
    found_names = {f.name for f in txt_files}
    missing = ALLOWED_FILES - found_names
    if missing:
        print(f"WARNING: {len(missing)} file(s) from whitelist not found in {BASE_DIR}:")
        for m in sorted(missing):
            print("  -", m)

    for path in txt_files:
        print(f"Analyzing: {path.name}")
        text = read_text_file(path)

        outputs = []
        # Single call if file is short, else chunk
        if len(text) <= MAX_CHARS_PER_CALL:
            outputs.append(call_model(client, MODEL_NAME, text))
        else:
            for chunk in iter_chunks(text, MAX_CHARS_PER_CALL):
                outputs.append(call_model(client, MODEL_NAME, chunk))

        # Save combined outputs
        out_path = write_analysis_txt(path, outputs)

        # Extract and save decisions from ALL chunks
        for idx, chunk_out in enumerate(outputs, start=1):
            decisions = extract_all_decisions(chunk_out)
            if decisions:
                append_decision_rows(DECISIONS_CSV, path.name, idx, decisions)

        print(f"  → Saved: {out_path.name} | Decisions captured from {len(outputs)} chunk(s)")

if __name__ == "__main__":
    main()
