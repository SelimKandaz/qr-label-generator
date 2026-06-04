# QRCC User Guide

## Overview
QRCC (QR Code Creator) converts pasted text into QR codes.
Each non-empty line is treated as one item and becomes one QR code image.
You can optionally generate a printable PDF sheet as well.

## Version
- Product: QRCC (QR Code Creator)
- Company: Open Source Utility
- Version: 1.0.0
- Build date: 2026-02-19

## Requirements
Install Python 3.10+ then install dependencies:

```bash
pip install qrcode[pil] pillow reportlab
```

## How to Use
1. Open QRCC.
2. Paste text into the box.
3. Each non-empty line becomes one QR code.
4. Adjust QR settings if needed.
5. Click Generate.
6. Outputs are written to the selected output folder under a run_ timestamp folder.

## Output Folder Structure
Outputs are written under an outputs folder next to the program by default:

- outputs/run_YYYYMMDD_HHMMSS/
  - qr_001.png
  - qr_002.png
  - qrcc_labels.pdf (optional)

## Scanner Reliability Tips
- For print, keep QR width at least 6 to 8 cm.
- Avoid glossy reflections for laser scanners.
- If scan is unreliable, increase box size and border.
- Use EC L for easiest scanning. Use EC M or Q if you expect damage on labels.

## Troubleshooting

### No module named 'qrcode'
Install dependencies again:

```bash
pip install qrcode[pil] pillow reportlab
```

### PDF generation fails
Make sure reportlab is installed:

```bash
pip install reportlab
```

## Support
For support, open a GitHub issue or modify the source for your own workflow.
