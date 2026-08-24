#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import xml.etree.ElementTree as ET
from pathlib import Path
import json, csv, time, sys, subprocess, shutil
from typing import Optional, List, Tuple

# =========================
# Configuration
# =========================
GROBID_URL = "http://localhost:8070/api/processFulltextDocument"

PDF_FOLDER = Path("./pdfs")
OUTPUT_FOLDER = Path("./outputs")
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

REQUEST_TIMEOUT = 120
MAX_RETRIES = 3

ENABLE_OCR_FALLBACK = True       # requires 'ocrmypdf' installed
OCR_TMP_DIR = OUTPUT_FOLDER / "_ocr_tmp"
OCR_TMP_DIR.mkdir(exist_ok=True)

TRY_PDFPLUMBER_TABLES = True
try:
    import pdfplumber  # type: ignore
    HAVE_PDFPLUMBER = True
except Exception:
    HAVE_PDFPLUMBER = False

from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams, LTTextContainer, LTTextBox, LTTextBoxHorizontal, LTTextLine, LTFigure

ns = {"tei": "http://www.tei-c.org/ns/1.0"}

# =========================
# Helpers
# =========================
def _norm(s: str) -> str:
    return " ".join(s.split()) if s else ""

def _txt(elem) -> str:
    return _norm("".join(elem.itertext()).strip()) if elem is not None else ""

def _lname(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag

def _aff_string(aff: dict) -> str:
    bits = [aff.get("department"), aff.get("laboratories"), aff.get("organization"), aff.get("address")]
    return ", ".join([b for b in bits if b])

def _aff_list_to_string(aff_list) -> str:
    vals = [_aff_string(a) for a in (aff_list or [])]
    vals = [v for v in vals if v]
    return " | ".join(vals)

def _has_cmd(cmd: str) -> bool:
    return shutil.which(cmd) is not None

# =========================
# Metadata extraction (GROBID)
# =========================
def extract_title(root: ET.Element) -> str:
    for xp in [
        ".//tei:teiHeader//tei:titleStmt/tei:title",
        ".//tei:sourceDesc//tei:biblStruct/tei:analytic/tei:title",
        ".//tei:title",
    ]:
        el = root.find(xp, ns)
        if el is not None and _txt(el):
            return _txt(el)
    return ""

def extract_abstract(root: ET.Element) -> str:
    for xp in [
        ".//tei:teiHeader//tei:fileDesc//tei:profileDesc//tei:abstract",
        ".//tei:sourceDesc//tei:biblStruct/tei:analytic/tei:abstract",
        ".//tei:text//tei:front//tei:abstract",
    ]:
        el = root.find(xp, ns)
        if el is not None and _txt(el):
            return _txt(el)
    return ""

def extract_authors_and_affils(root: ET.Element):
    authors = []
    author_paths = [
        ".//tei:sourceDesc//tei:biblStruct/tei:analytic/tei:author",
        ".//tei:teiHeader//tei:fileDesc//tei:titleStmt/tei:author",
    ]
    for ap in author_paths:
        for a in root.findall(ap, ns):
            pers = a.find(".//tei:persName", ns)
            given = _txt(pers.find(".//tei:forename", ns)) if pers is not None else ""
            surname = _txt(pers.find(".//tei:surname", ns)) if pers is not None else ""
            full = _txt(pers) if pers is not None else (given + " " + surname).strip()
            orcid_el = a.find(".//tei:idno[@type='ORCID']", ns)
            orcid = _txt(orcid_el) if orcid_el is not None else ""

            # Affiliations
            affils = []
            for aff in a.findall(".//tei:affiliation", ns):
                orgs = [_txt(x) for x in aff.findall(".//tei:orgName", ns) if _txt(x)]
                dept = _txt(aff.find(".//tei:orgName[@type='department']", ns))
                labs = [_txt(x) for x in aff.findall(".//tei:orgName[@type='laboratory']", ns) if _txt(x)]
                addr = _txt(aff.find(".//tei:address", ns))
                affils.append({
                    "organization": "; ".join(orgs) if orgs else "",
                    "department": dept,
                    "laboratories": "; ".join(labs) if labs else "",
                    "address": addr
                })

            # Corresponding author signal
            is_corresp = (a.attrib.get("role") == "corresp")
            email = ""
            email_el = a.find(".//tei:email", ns)
            if email_el is not None and _txt(email_el):
                email = _txt(email_el)
                is_corresp = True

            authors.append({
                "full_name": full or "Unknown",
                "given": given,
                "family": surname,
                "orcid": orcid,
                "email": email,
                "corresponding": is_corresp,
                "affiliations": affils or []
            })
        if authors:
            break
    return authors

def grobid_header_block(title: str, abstract: str, authors: list) -> str:
    lines = [f"TITLE: {title or 'Unknown'}"]
    if authors:
        for i, a in enumerate(authors, 1):
            corresp_flag = " [CORRESPONDING]" if a.get("corresponding") else ""
            aff_str = _aff_list_to_string(a.get("affiliations"))
            line = f"AUTHOR {i}: {a.get('full_name','Unknown')}{corresp_flag}"
            if a.get("orcid"):
                line += f" (ORCID: {a['orcid']})"
            if a.get("email"):
                line += f" <{a['email']}>"
            lines.append(line)
            if aff_str:
                lines.append(f"  Affiliations: {aff_str}")
    else:
        lines.append("AUTHORS: Unknown")
    if abstract:
        lines.append("\nABSTRACT:\n" + abstract)
    lines.append("=" * 80)
    return "\n".join(lines) + "\n\n"

# =========================
# Column-preserving full text
# =========================
def pdftotext_layout(pdf_path: Path) -> Optional[str]:
    """Use Poppler's pdftotext -layout if available (best column preservation)."""
    if not _has_cmd("pdftotext"):
        return None
    try:
        # '-layout' preserves columns; '-nopgbrk' avoids form feed chars
        result = subprocess.run(
            ["pdftotext", "-layout", "-nopgbrk", "-q", str(pdf_path), "-"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        txt = result.stdout.decode("utf-8", errors="replace")
        return txt if txt.strip() else None
    except subprocess.CalledProcessError:
        return None

def _collect_textboxes(layout_obj) -> List[Tuple[float,float,float,float,str]]:
    """Collect (x0, y0, x1, y1, text) from layout recursively."""
    boxes = []
    if isinstance(layout_obj, (LTTextBox, LTTextBoxHorizontal, LTTextLine)):
        t = layout_obj.get_text()
        if t and t.strip():
            x0, y0, x1, y1 = layout_obj.bbox
            boxes.append((x0, y0, x1, y1, t))
    elif isinstance(layout_obj, LTFigure):
        for o in layout_obj:
            boxes.extend(_collect_textboxes(o))
    else:
        try:
            for o in layout_obj:
                boxes.extend(_collect_textboxes(o))
        except TypeError:
            pass
    return boxes

def _split_into_columns(boxes, page_width, max_cols=3):
    """
    Heuristic column splitter:
    - Compute x-center for each box
    - Sort by x; find large gaps (> 0.12 * page_width) as column separators
    - Cap at max_cols
    """
    if not boxes:
        return [boxes]

    centers = sorted([( (b[0]+b[2])/2.0, idx ) for idx, b in enumerate(boxes)], key=lambda x: x[0])
    xs = [c for c, _ in centers]
    gaps = []
    for i in range(1, len(xs)):
        gaps.append((xs[i]-xs[i-1], i))
    # sort gaps by size descending
    gaps_sorted = sorted(gaps, key=lambda g: g[0], reverse=True)

    # choose up to max_cols-1 biggest gaps that exceed threshold
    thresh = 0.12 * page_width
    cut_indices = sorted([i for (g,i) in gaps_sorted if g >= thresh][:max_cols-1])

    # build column index for each box by slicing centers at cuts
    col_assign = {}
    prev = 0
    col_id = 0
    for cut in cut_indices + [len(centers)]:
        for _, idx in centers[prev:cut]:
            col_assign[idx] = col_id
        col_id += 1
        prev = cut

    columns = [[] for _ in range(col_id)]
    for idx, b in enumerate(boxes):
        columns[col_assign.get(idx, min(col_id-1, 0))].append(b)
    return columns

def extract_text_preserve_columns(pdf_path: Path) -> str:
    """
    If pdftotext -layout is available, use it.
    Otherwise, use pdfminer page layouts:
    - group text boxes by column (x position)
    - order columns left->right
    - inside each column, order blocks top->bottom (y descending)
    """
    # Try Poppler first
    txt = pdftotext_layout(pdf_path)
    if txt is not None:
        return txt

    laparams = LAParams(
        line_overlap=0.5,
        char_margin=2.0,
        line_margin=0.4,
        word_margin=0.1,
        boxes_flow=None
    )

    pages_out = []
    for page_layout in extract_pages(str(pdf_path), laparams=laparams):
        # page size from layout
        try:
            page_width = float(page_layout.bbox[2] - page_layout.bbox[0])
        except Exception:
            page_width = 612.0  # fallback (US Letter width in points)

        boxes = _collect_textboxes(page_layout)
        if not boxes:
            pages_out.append("")  # could be images only
            continue

        # split into columns, keep left->right
        columns = _split_into_columns(boxes, page_width)

        # for each column, sort by top (y1) descending, then x0
        col_texts = []
        for col in columns:
            col_sorted = sorted(col, key=lambda b: (-b[3], b[0]))
            text = []
            last_y = None
            for (x0, y0, x1, y1, t) in col_sorted:
                # normalize line endings
                t = t.replace("\r\n", "\n").replace("\r", "\n")
                # pdfminer already has lines; just append
                text.append(t.strip("\n"))
                last_y = y1
            col_texts.append("\n".join(text))

        page_text = "\n\n".join(col_texts)
        pages_out.append(page_text.strip())

    return ("\n\n=== Page Break ===\n\n").join([p for p in pages_out if p])

# =========================
# OCR + tables (optional)
# =========================
def ocr_pdf_if_needed(pdf_path: Path) -> Optional[Path]:
    if not ENABLE_OCR_FALLBACK or not _has_cmd("ocrmypdf"):
        return None
    # quick probe: if column extractor returns too little, OCR
    probe = extract_text_preserve_columns(pdf_path)
    if len(probe.strip()) >= 500:
        return None
    ocr_out = OCR_TMP_DIR / (pdf_path.stem + ".ocr.pdf")
    try:
        print(f"🩺 Running OCR for {pdf_path.name} …")
        subprocess.run(
            ["ocrmypdf", "--force-ocr", "--skip-text", "--optimize", "0",
             str(pdf_path), str(ocr_out)],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return ocr_out
    except subprocess.CalledProcessError as e:
        print(f"OCR failed for {pdf_path.name}: {e}", file=sys.stderr)
        return None

def append_tables_if_any(pdf_path: Path, text_out: str) -> str:
    if not (TRY_PDFPLUMBER_TABLES and HAVE_PDFPLUMBER):
        return text_out
    try:
        lines = [text_out.rstrip(), "\n\n# Extracted Tables (best-effort)\n"]
        found_any = False
        with pdfplumber.open(str(pdf_path)) as pdf:
            for pidx, page in enumerate(pdf.pages, 1):
                try:
                    tables = page.extract_tables()
                except Exception:
                    tables = []
                for tidx, tbl in enumerate(tables, 1):
                    if not tbl:
                        continue
                    found_any = True
                    lines.append(f"Table p{pidx}.{tidx}:")
                    for row in tbl:
                        row = [c.strip() if c else "" for c in row]
                        lines.append(" | ".join(row))
                    lines.append("")
        return "\n".join(lines) if found_any else text_out
    except Exception as e:
        print(f"pdfplumber tables failed on {pdf_path.name}: {e}", file=sys.stderr)
        return text_out

# =========================
# GROBID call
# =========================
def call_grobid(pdf_path: Path) -> Optional[ET.Element]:
    response = None
    for attempt in range(MAX_RETRIES):
        with open(pdf_path, "rb") as f:
            try:
                response = requests.post(
                    GROBID_URL,
                    files={"input": f},
                    data={
                        "consolidateHeader": 1,
                        "consolidateCitations": 1,
                        "includeRawAffiliations": 1,
                        "includeRawCitations": 1,
                        "teiCoordinates": "persName,ref,biblStruct,figure,head,label,p,formula,table",
                    },
                    timeout=REQUEST_TIMEOUT,
                )
            except requests.RequestException as e:
                print(f"Request error on {pdf_path.name}: {e}", file=sys.stderr)
                response = None

        if response is not None and response.status_code == 200 and response.text.strip():
            try:
                return ET.fromstring(response.text)
            except ET.ParseError:
                print(f"⚠️ XML parse error for {pdf_path.name}", file=sys.stderr)
                return None

        wait = 2 ** attempt
        print(f"… retry {attempt+1}/{MAX_RETRIES} for {pdf_path.name} (waiting {wait}s)")
        time.sleep(wait)

    print(f"❌ GROBID failed: {pdf_path.name} — Status {getattr(response, 'status_code', 'N/A')}")
    return None

# =========================
# Per-file processing
# =========================
def process_pdf(pdf_path: Path):
    txt_path = OUTPUT_FOLDER / (pdf_path.stem + ".txt")
    meta_path = OUTPUT_FOLDER / (pdf_path.stem + ".metadata.json")

    print(f"Processing: {pdf_path.name}")

    if txt_path.exists() and meta_path.exists():
        print(f"⏩ Skipping {pdf_path.name} (already processed)")
        return None

    # 1) Metadata via GROBID (no XML persisted)
    root = call_grobid(pdf_path)
    title = abstract = ""
    authors = []
    if root is not None:
        title = extract_title(root)
        abstract = extract_abstract(root)
        authors = extract_authors_and_affils(root)

    # 2) Full text with column preservation (+ OCR fallback)
    candidate_pdf = pdf_path
    ocr_pdf = ocr_pdf_if_needed(pdf_path)
    if ocr_pdf:
        candidate_pdf = ocr_pdf
    full_text = extract_text_preserve_columns(candidate_pdf)

    # 2b) Optional: append tables
    full_text = append_tables_if_any(candidate_pdf, full_text)

    # 3) Write metadata JSON
    metadata = {
        "filename": pdf_path.name,
        "title": title,
        "abstract": abstract,
        "authors": authors,
        "used_ocr": bool(ocr_pdf),
        "column_method": "pdftotext-layout" if _has_cmd("pdftotext") else "pdfminer-column-heuristic",
    }
    meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    # 4) Write TXT (prepend header if we have metadata)
    header = grobid_header_block(title, abstract, authors) if (title or authors or abstract) else ""
    txt_path.write_text(header + (full_text or "").rstrip() + "\n", encoding="utf-8")

    print(f"✅ Saved: {meta_path.name}, {txt_path.name}")

    # CSV row
    author_flat = "; ".join([a["full_name"] for a in authors]) if authors else ""
    corresp_names = "; ".join([a["full_name"] for a in authors if a.get("corresponding")])
    corresp_affs = "; ".join([
        _aff_list_to_string(a.get("affiliations"))
        for a in authors if a.get("corresponding")
    ])
    return {
        "filename": pdf_path.name,
        "title": title,
        "authors": author_flat,
        "corresponding_authors": corresp_names,
        "corresponding_affiliations": corresp_affs,
        "has_abstract": bool(abstract),
        "used_ocr": bool(ocr_pdf),
        "column_method": "pdftotext-layout" if _has_cmd("pdftotext") else "pdfminer-column-heuristic",
    }

# =========================
# Main
# =========================
def main():
    csv_rows = []
    for pdf_file in PDF_FOLDER.glob("*.pdf"):
        row = process_pdf(pdf_file)
        if row:
            csv_rows.append(row)

    if csv_rows:
        csv_path = OUTPUT_FOLDER / "metadata_aggregate.csv"
        fieldnames = [
            "filename",
            "title",
            "authors",
            "corresponding_authors",
            "corresponding_affiliations",
            "has_abstract",
            "used_ocr",
            "column_method",
        ]
        write_header = not csv_path.exists()
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerows(csv_rows)
        print(f"🧾 Updated: {csv_path.name}")

    print("🎯 All PDFs processed.")

if __name__ == "__main__":
    main()
