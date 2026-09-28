# QR Label Generator (QRCC)

Generates QR and Code128 labels and printable PDF label sheets for inventory and asset tracking.

## Desktop app

```bash
pip install -r requirements.txt
python src/QRCC_v1_3_0.py
```

- One QR per line, or several lines grouped into one QR
- PNG and PDF sheet export
- Code128 barcodes
- Avery-style label layouts
- Built-in user guide

## Command line

Generate labels from a CSV:

```bash
python src/qr_label_generator.py examples/assets.csv --out output
```

The repo includes sample data only.

## License

MIT
