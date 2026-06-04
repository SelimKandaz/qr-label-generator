#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path

import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def make_qr(value: str, path: Path):
    img = qrcode.make(value)
    img.save(path)

def main():
    parser = argparse.ArgumentParser(description="Generate QR labels from a CSV file.")
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--out", type=Path, default=Path("output"))
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    qr_dir = args.out / "qr"
    qr_dir.mkdir(exist_ok=True)

    rows = list(csv.DictReader(args.csv_file.open(encoding="utf-8")))
    for row in rows:
        make_qr(row["value"], qr_dir / f"{row['asset_id']}.png")

    pdf_path = args.out / "label-sheet.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    x, y = 72, 720
    for row in rows:
        img_path = qr_dir / f"{row['asset_id']}.png"
        c.drawImage(str(img_path), x, y - 72, width=72, height=72)
        c.drawString(x + 85, y - 25, row["label"])
        c.drawString(x + 85, y - 45, row["value"])
        y -= 100
        if y < 120:
            c.showPage()
            y = 720
    c.save()
    print(f"Generated labels in {args.out}")

if __name__ == "__main__":
    main()
