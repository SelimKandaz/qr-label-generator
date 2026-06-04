# QR Label Generator

A lightweight Python utility for generating QR labels and inventory-ready label sheets from CSV asset data.

## Features

- Generate QR labels from CSV input
- Produce individual PNG labels
- Produce a printable PDF label sheet
- Sanitize asset IDs before using them as filenames
- Validate required CSV columns
- Use fake sample data for public demonstration

## Quick start

```bash
pip install -r requirements.txt
python src/qr_label_generator.py examples/assets.csv --out output
```

## Test

```bash
python -m pytest
```

## Technology focus

Python, QR generation, PDF layout generation, CSV-driven operations tooling and inventory workflows.
