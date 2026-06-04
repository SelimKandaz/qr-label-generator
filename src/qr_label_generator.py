#!/usr/bin/env python3
import argparse
import csv
import re
from pathlib import Path

import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

REQUIRED_COLUMNS = {"asset_id", "label", "value"}

def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return cleaned.strip("._") or "label"

def read_assets(csv_file: Path):
    with csv_file.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV file has no header row.")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"CSV missing required columns: {', '.join(sorted(missing))}")
        return list(reader)

def make_qr(value: str, path: Path):
    img = qrcode.make(value)
    img.save(path)

def generate_labels(csv_file: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    qr_dir = out_dir / "qr"
    qr_dir.mkdir(exist_ok=True)

    rows = read_assets(csv_file)
    if not rows:
        raise ValueError("CSV contains no asset rows.")

    for row in rows:
        make_qr(row["value"], qr_dir / (safe_filename(row["asset_id"]) + ".png"))

    pdf_path = out_dir / "label-sheet.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    x, y = 72, 720

    for row in rows:
        img_path = qr_dir / (safe_filename(row["asset_id"]) + ".png")
        c.drawImage(str(img_path), x, y - 72, width=72, height=72)
        c.drawString(x + 85, y - 25, row["label"])
        c.drawString(x + 85, y - 45, row["value"])
        y -= 100
        if y < 120:
            c.showPage()
            y = 720

    c.save()
    return pdf_path, qr_dir

def main():
    parser = argparse.ArgumentParser(description="Generate QR labels from a CSV file.")
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--out", type=Path, default=Path("output"))
    args = parser.parse_args()
    pdf_path, qr_dir = generate_labels(args.csv_file, args.out)
    print(f"Generated QR images in: {qr_dir}")
    print(f"Generated label sheet: {pdf_path}")

if __name__ == "__main__":
    main()
