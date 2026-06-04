# QR Label Generator

A lightweight Python utility for generating QR labels and inventory-ready label sheets.

This repository is a sanitized portfolio version for asset labeling, inventory workflows and simple operations automation.

## Features

- Generate QR labels from CSV input
- Produce individual PNG labels
- Produce a simple PDF sheet layout
- Use fake sample data for public demonstration
- Keep output files out of Git by default

## Quick start

```bash
pip install -r requirements.txt
python src/qr_label_generator.py examples/assets.csv --out output
```

## Technology focus

- Python
- QR code generation
- PDF report/layout generation
- CSV-driven operations tooling
- Inventory and asset tracking workflows

## Portfolio note

This project demonstrates practical internal-tool design: small utilities that reduce repeated manual work in technical operations.
