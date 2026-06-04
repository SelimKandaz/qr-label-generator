# Customization Guide

This project can be adapted for inventory and asset label workflows.

## Common customization points

- CSV columns
- QR payload format
- Code128 barcode format
- PDF label size and spacing
- Output folder naming
- Branding text
- Avery-style sheet layout

## Start here

- `src/qr_label_generator.py` for the CLI utility
- `src/QRCC_v1_3_0.py` for the desktop GUI
- `examples/assets.csv` for sample input

## Keep local

Keep private files and generated production outputs outside the repository.
