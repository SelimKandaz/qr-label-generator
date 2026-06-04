# QR Label Generator / QRCC

A Python QR and Code128 label generator for inventory, asset labeling and operations workflows.

This repository now includes two layers:

1. `src/qr_label_generator.py`  
   A small CLI utility for CSV-driven QR label generation.

2. `src/QRCC_v1_3_0.py`  
   The original full QRCC v1.3.0 desktop GUI application, sanitized for public open-source use.

## Full GUI application

Run the QRCC desktop app:

```bash
pip install -r requirements.txt
python src/QRCC_v1_3_0.py
```

The GUI supports:

- One QR per line
- Grouping multiple lines into one QR
- QR PNG export
- PDF sheet export
- Code128 barcode output
- Avery-style label workflows
- User guide access from inside the app

## CLI utility

Run the lightweight CSV-driven utility:

```bash
python src/qr_label_generator.py examples/assets.csv --out output
```

## Requirements

```bash
pip install -r requirements.txt
```

## Open-source note

This project is published as a sanitized open-source utility. It contains fake sample data only. Do not commit private asset lists, customer records, real serial-number batches or internal company output files.

## License

MIT
