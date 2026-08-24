#!/usr/bin/env python

# This tool takes a directory of PDF files and converts 
# them to utf-8 text files, which it places in a separate
# directory.

import requests
import xml.etree.ElementTree as ET
from pathlib import Path
 
# GROBID API endpoint (must have Docker GROBID running)
GROBID_URL = "http://localhost:8070/api/processFulltextDocument"
 
# Your Mac paths
PDF_FOLDER    = Path("./PDFs")
OUTPUT_FOLDER = Path("./TXTs")
 
# Make sure output folder exists
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
 
# Loop through all PDFs in the input folder
for pdf_file in PDF_FOLDER.glob("*.pdf"):
    print(f"Processing: {pdf_file.name}")
 
    # Send PDF to GROBID
    with open(pdf_file, "rb") as f:
        response = requests.post(GROBID_URL, files={"input": f})
    
    if response.status_code != 200:
        print(f"X Failed: {pdf_file.name} — Status {response.status_code}")
        continue
 
    # Save TEI XML
    # tei_path = OUTPUT_FOLDER / (pdf_file.stem + ".tei.xml")
    # tei_path.write_text(response.text, encoding="utf-8")
 
    # Extract plain text
    root = ET.fromstring(response.text)
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}
    text = "\n".join(
        line.strip()
        for line in root.itertext()
        if line.strip()
    )
    
    txt_path = OUTPUT_FOLDER / (pdf_file.stem + ".txt")
    txt_path.write_text(text, encoding="utf-8")
 
    print(f"Saved: {txt_path}")
 
print("All PDFs processed.")

 
