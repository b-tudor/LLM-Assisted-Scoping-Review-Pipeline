#!/usr/bin/env python3
"""
Report file length in characters and estimated tokens, sorted descending.
"""

from pathlib import Path

# ======= CONFIGURATION =======
BASE_DIR = Path("./outputs")
# =============================

def estimate_tokens(text: str) -> int:
    """
    Roughly estimate token count from text length.
    Assumes ~4 characters per token on average.
    """
    return round(len(text) / 4)

def main():
    txt_files = sorted(BASE_DIR.glob("*.txt"))

    if not txt_files:
        print(f"No .txt files found in {BASE_DIR}")
        return

    file_data = []
    for path in txt_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        char_count = len(text)
        token_count = estimate_tokens(text)
        file_data.append((path.name, char_count, token_count))

    # Sort descending by char_count
    file_data.sort(key=lambda x: x[1], reverse=True)

    print(f"{'File Name':40} {'Chars':>10} {'Est. Tokens':>12}")
    print("-" * 64)
    for name, char_count, token_count in file_data:
        print(f"{name:40} {char_count:10} {token_count:12}")

if __name__ == "__main__":
    main()
