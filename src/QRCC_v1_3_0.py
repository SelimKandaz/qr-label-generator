# QRCC (QR Code Creator) - General purpose QR generator
#
# Converts each non-empty line into its own QR code PNG and optional PDF sheet.
#
# Install:
#   pip install qrcode[pil] pillow reportlab
#
# Run:
#   python QRCC_v1_3_0.py

from __future__ import annotations

import os
import sys
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.simpledialog as simpledialog

import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from reportlab.lib.units import inch


# -------------------- Application Metadata --------------------
__appname__ = "QRCC"
__product_name__ = "QR Code Creator"
__company__ = "Open Source Utility"
__version__ = "1.3.0"
__build_date__ = "2026-02-19"
# --------------------------------------------------------------


@dataclass
class QRCCSettings:
    line_ending: str = "\n"
    add_trailing_newline: bool = False

    # QR sizing and scan reliability
    error_correction: str = "L"  # L scans easiest
    box_size: int = 22
    border: int = 8

    # Text handling
    strip_lines: bool = True
    skip_blank_lines: bool = True


def get_base_dir() -> Path:
    """Return app directory (exe folder if frozen, else script folder)."""
    return Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent


def safe_open_path(p: Path) -> None:
    """Open a file or folder with the OS default handler."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(p))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            os.system(f'open "{p}"')
        else:
            os.system(f'xdg-open "{p}"')
    except Exception:
        try:
            webbrowser.open(p.as_uri())
        except Exception:
            pass


def open_user_guide() -> None:
    base = get_base_dir()
    candidates = [
        base / "USER_GUIDE_QRCC.md",
        base / "USER_GUIDE.md",
        base / "README.md",
    ]
    for c in candidates:
        if c.exists():
            safe_open_path(c)
            return
    messagebox.showinfo(__appname__, "User guide file was not found next to the program.")


def show_about() -> None:
    msg = (
        f"{__appname__} ({__product_name__}) v{__version__}\n"
        f"{__company__}\n\n"
        "General purpose QR generator.\n"
        "Each non-empty line becomes a QR item. You can also group N lines per QR."
    )
    messagebox.showinfo("About", msg)


def make_payload(lines: list[str], cfg: QRCCSettings) -> str:
    payload = cfg.line_ending.join(lines)
    if cfg.add_trailing_newline:
        payload += cfg.line_ending
    return payload


def parse_lines(text: str, cfg: QRCCSettings) -> list[str]:
    # Normalize newlines and split
    raw_lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out: list[str] = []
    for line in raw_lines:
        if cfg.strip_lines:
            line = line.strip()
        if cfg.skip_blank_lines and not line:
            continue
        out.append(line)
    return out

def group_lines(lines: list[str], per_qr: int, cfg: QRCCSettings) -> tuple[list[str], list[str]]:
    """Group lines into payloads of size per_qr.
    Returns (payloads, labels_for_pdf).
    """
    if per_qr <= 1:
        return lines[:], lines[:]

    payloads: list[str] = []
    labels: list[str] = []
    total = len(lines)
    i = 0
    while i < total:
        chunk = lines[i : i + per_qr]
        payloads.append(make_payload(chunk, cfg))
        # PDF label: show index range and preview first/last
        start = i + 1
        end = min(i + per_qr, total)
        preview_first = chunk[0]
        preview_last = chunk[-1] if len(chunk) > 1 else ""
        if len(chunk) == 1:
            label = f"Lines {start}-{end}: {preview_first}"
        else:
            label = f"Lines {start}-{end}: {preview_first} ... {preview_last}"
        labels.append(label)
        i += per_qr
    return payloads, labels


def make_qr_image(payload: str, cfg: QRCCSettings):
    ec_map = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H,
    }
    qr = qrcode.QRCode(
        version=None,
        error_correction=ec_map[cfg.error_correction],
        box_size=cfg.box_size,
        border=cfg.border,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")


def save_qr_pngs(payloads: list[str], out_dir: Path, cfg: QRCCSettings) -> list[Path]:
    """Save one PNG per payload."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for i, payload in enumerate(payloads, start=1):
        img = make_qr_image(payload, cfg)
        p = out_dir / f"qr_{i:03d}.png"
        img.save(p)
        paths.append(p)
    return paths



def save_qr_pdf_avery_5160(png_paths: list[Path], labels: list[str], out_pdf: Path):
    """Avery 5160 / 8160 layout (Letter, 3 columns x 10 rows, 2-5/8" x 1").
    This is a common warehouse label sheet format.
    """
    c = canvas.Canvas(str(out_pdf), pagesize=letter)
    W, H = letter

    # Avery 5160 spec (in inches)
    left_margin = 0.1875 * inch
    top_margin = 0.5 * inch
    label_w = 2.625 * inch
    label_h = 1.0 * inch
    h_pitch = 2.75 * inch
    v_pitch = 1.0 * inch

    cols = 3
    rows = 10

    # QR drawing sizes inside a label
    qr_size = 0.82 * inch
    pad_x = 0.12 * inch
    pad_y = 0.08 * inch

    x0 = left_margin
    y0 = H - top_margin - label_h  # top-left label bottom y

    for idx, p in enumerate(png_paths):
        page_index = idx // (cols * rows)
        pos_in_page = idx % (cols * rows)

        if idx > 0 and pos_in_page == 0:
            c.showPage()

        r = pos_in_page // cols
        col = pos_in_page % cols

        x = x0 + col * h_pitch
        y = y0 - r * v_pitch

        # QR
        c.drawImage(
            str(p),
            x + pad_x,
            y + pad_y,
            width=qr_size,
            height=qr_size,
            preserveAspectRatio=True,
            mask="auto",
        )

        # Text (label snippet)
        c.setFont("Helvetica", 7)
        label = labels[idx].replace("\n", " ")
        if len(label) > 34:
            label = label[:31] + "..."
        c.drawString(x + pad_x + qr_size + 0.10 * inch, y + label_h / 2, label)

        # Filename small
        c.setFont("Helvetica", 6)
        c.drawString(x + pad_x + qr_size + 0.10 * inch, y + 0.18 * inch, p.name)

    c.save()


def save_qr_pdf_sheet(png_paths: list[Path], labels: list[str], out_pdf: Path):
    """2 columns per page. Each QR gets a filename and a short label line under it."""
    c = canvas.Canvas(str(out_pdf), pagesize=letter)
    W, H = letter

    margin = 0.5 * inch
    col_w = (W - 2 * margin) / 2
    row_h = 3.8 * inch

    x_positions = [margin, margin + col_w]
    y = H - margin
    col = 0

    for idx, p in enumerate(png_paths):
        if col == 0:
            y -= row_h
            if y < margin:
                c.showPage()
                y = H - margin - row_h

        x = x_positions[col]
        img_size = 3.1 * inch

        c.drawImage(
            str(p),
            x,
            y + 0.45 * inch,
            width=img_size,
            height=img_size,
            preserveAspectRatio=True,
            mask="auto",
        )

        c.setFont("Helvetica", 9)
        # Filename
        c.drawString(x, y + 0.27 * inch, p.name)

        # Label (truncate for PDF readability)
        label = labels[idx]
        label = label.replace("\n", " ")
        if len(label) > 52:
            label = label[:49] + "..."
        c.drawString(x, y + 0.10 * inch, label)

        col = 1 - col

    c.save()



def save_code128_pdf_sheet(payloads: list[str], labels: list[str], out_pdf: Path):
    """Standard (2-column) Code128 sheet on Letter.
    Note: Code128 is best for single-line values. For grouped payloads, newlines are replaced with spaces.
    """
    c = canvas.Canvas(str(out_pdf), pagesize=letter)
    W, H = letter

    margin = 0.55 * inch
    col_w = (W - 2 * margin) / 2
    row_h = 1.7 * inch

    x_positions = [margin, margin + col_w]
    y = H - margin
    col = 0

    for idx, payload in enumerate(payloads):
        if col == 0:
            y -= row_h
            if y < margin:
                c.showPage()
                y = H - margin - row_h

        x = x_positions[col]

        # Normalize payload for 1D barcode
        p1d = payload.replace("\r\n", "\n").replace("\r", "\n").replace("\n", " ").strip()

        # Create barcode
        bc = code128.Code128(p1d, barHeight=0.65 * inch, humanReadable=False)

        # Draw barcode
        bc.drawOn(c, x, y + 0.55 * inch)

        # Label snippet
        c.setFont("Helvetica", 8)
        label = labels[idx].replace("\n", " ")
        if len(label) > 70:
            label = label[:67] + "..."
        c.drawString(x, y + 0.35 * inch, label)

        # Payload snippet
        c.setFont("Helvetica", 7)
        ptxt = p1d
        if len(ptxt) > 80:
            ptxt = ptxt[:77] + "..."
        c.drawString(x, y + 0.18 * inch, ptxt)

        col = 1 - col

    c.save()


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # Corporate look and feel
        try:
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("TLabel", font=("Segoe UI", 10))
            style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
            style.configure("SubHeader.TLabel", font=("Segoe UI", 10))
            style.configure("TButton", font=("Segoe UI", 10))
            style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        except Exception:
            pass

        # Optional icon if app.ico exists
        try:
            ico = get_base_dir() / "app.ico"
            if ico.exists():
                self.iconbitmap(str(ico))
        except Exception:
            pass

        self.title(f"{__appname__} v{__version__}")
        self.geometry("920x680")
        self.minsize(880, 620)

        base_dir = get_base_dir()
        self.out_dir = tk.StringVar(value=str(base_dir / "outputs"))

        self.make_pdf = tk.BooleanVar(value=True)
        self.make_code128 = tk.BooleanVar(value=False)
        self.pdf_layout = tk.StringVar(value="Standard (2-column)")
        self.strip_lines = tk.BooleanVar(value=True)
        self.skip_blank = tk.BooleanVar(value=True)

        self.box = tk.IntVar(value=22)
        self.border = tk.IntVar(value=8)
        self.ec = tk.StringVar(value="L")

        self.lines_per_qr = tk.IntVar(value=1)

        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)

        # Menu bar
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Generate", command=self._generate)
        file_menu.add_command(label="Clear", command=lambda: self.txt.delete("1.0", "end"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="User Guide", command=open_user_guide)
        help_menu.add_command(label="About", command=show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)

        # Header (top)
        header = ttk.Frame(frm)
        header.pack(side="top", fill="x", pady=(0, 10))

        ttk.Label(header, text=__product_name__, style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text=f"{__company__}   |   Version {__version__}   |   Build {__build_date__}",
            style="SubHeader.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        # Footer (bottom): settings, output, buttons, status
        footer = ttk.Frame(frm)
        footer.pack(side="bottom", fill="x")

        # Status bar at very bottom
        self.status = ttk.Label(footer, text="Ready.", relief="sunken", anchor="w", padding=(6, 4))
        self.status.pack(side="bottom", fill="x", pady=(6, 0))

        hint = (
            "Tip: Each non-empty line becomes one item. Set Lines per QR to bundle multiple lines into one QR.\n"
            "For print, keep QR width at least 6 to 8 cm. Use Help > User Guide for troubleshooting."
        )
        ttk.Label(footer, text=hint).pack(side="bottom", anchor="w", pady=(6, 0))

        btns = ttk.Frame(footer)
        btns.pack(side="bottom", fill="x", pady=(8, 0))

        ttk.Button(btns, text="Generate", command=self._generate).pack(side="left")
        ttk.Button(btns, text="Clear", command=lambda: self.txt.delete("1.0", "end")).pack(side="left", padx=8)
        ttk.Button(btns, text="Paste", command=self._paste).pack(side="left")

        out = ttk.LabelFrame(footer, text="Output", padding=10)
        out.pack(side="bottom", fill="x", pady=(10, 0))

        r3 = ttk.Frame(out)
        r3.pack(fill="x")

        ttk.Label(r3, text="Output folder:").pack(side="left")
        ttk.Entry(r3, textvariable=self.out_dir).pack(side="left", fill="x", expand=True, padx=8)
        ttk.Button(r3, text="Browse", command=self._browse_out).pack(side="left")

        txtopt = ttk.LabelFrame(footer, text="Text handling", padding=10)
        txtopt.pack(side="bottom", fill="x", pady=(10, 0))

        r2 = ttk.Frame(txtopt)
        r2.pack(fill="x", pady=2)
        ttk.Checkbutton(r2, text="Strip spaces around each line", variable=self.strip_lines).pack(side="left")
        ttk.Checkbutton(r2, text="Skip blank lines", variable=self.skip_blank).pack(side="left", padx=(20, 0))

        opt = ttk.LabelFrame(footer, text="QR settings", padding=10)
        opt.pack(side="bottom", fill="x", pady=(10, 0))

        r1 = ttk.Frame(opt)
        r1.pack(fill="x", pady=2)

        ttk.Label(r1, text="Box size:").pack(side="left")
        ttk.Spinbox(r1, from_=6, to=60, textvariable=self.box, width=6).pack(side="left", padx=8)

        ttk.Label(r1, text="Border:").pack(side="left", padx=(20, 0))
        ttk.Spinbox(r1, from_=2, to=20, textvariable=self.border, width=6).pack(side="left", padx=8)

        ttk.Label(r1, text="EC:").pack(side="left", padx=(20, 0))
        ttk.Combobox(r1, values=["L", "M", "Q", "H"], textvariable=self.ec, width=4, state="readonly").pack(side="left", padx=8)

        ttk.Label(r1, text="Lines per QR:").pack(side="left", padx=(20, 0))
        ttk.Spinbox(r1, from_=1, to=5000, textvariable=self.lines_per_qr, width=8).pack(side="left", padx=8)

        ttk.Checkbutton(r1, text="Create PDF sheet", variable=self.make_pdf).pack(side="left", padx=(20, 0))

        ttk.Checkbutton(r1, text="Create Code128 (1D) PDF", variable=self.make_code128).pack(side="left", padx=(14, 0))

        ttk.Label(r1, text="PDF layout:").pack(side="left", padx=(20, 0))
        ttk.Combobox(
            r1,
            values=["Standard (2-column)", "Avery 5160 (3x10 labels)"],
            textvariable=self.pdf_layout,
            width=24,
            state="readonly",
        ).pack(side="left", padx=8)

        # Middle content (expands): text area with scrollbar
        ttk.Label(frm, text="Paste text here (each line becomes one QR item):").pack(anchor="w")

        text_frame = ttk.Frame(frm)
        text_frame.pack(side="top", fill="both", expand=True, pady=(6, 10))

        yscroll = ttk.Scrollbar(text_frame, orient="vertical")
        yscroll.pack(side="right", fill="y")

        self.txt = tk.Text(text_frame, height=18, wrap="word", yscrollcommand=yscroll.set)
        self.txt.pack(side="left", fill="both", expand=True)
        yscroll.config(command=self.txt.yview)

    def _paste(self):
        try:
            data = self.clipboard_get()
        except tk.TclError:
            return
        self.txt.insert("insert", data)

    def _browse_out(self):
        d = filedialog.askdirectory(initialdir=self.out_dir.get() or str(Path.cwd()))
        if d:
            self.out_dir.set(d)

    def _generate(self):
        raw = self.txt.get("1.0", "end").strip()
        if not raw:
            messagebox.showwarning("Empty", "Text box is empty.")
            return

        cfg = QRCCSettings(
            error_correction=str(self.ec.get()),
            box_size=int(self.box.get()),
            border=int(self.border.get()),
            strip_lines=bool(self.strip_lines.get()),
            skip_blank_lines=bool(self.skip_blank.get()),
        )

        lines = parse_lines(raw, cfg)
        if not lines:
            messagebox.showerror("No lines", "No usable lines found. Check blank line settings.")
            return

        out_root = Path(self.out_dir.get()).expanduser().resolve()
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = out_root / f"run_{stamp}"
        run_dir.mkdir(parents=True, exist_ok=True)

        try:
            per_qr = int(self.lines_per_qr.get() or 1)
            payloads, labels = group_lines(lines, per_qr, cfg)

            pngs = save_qr_pngs(payloads, run_dir, cfg)

            pdf_path = None
            if self.make_pdf.get():
                if self.pdf_layout.get().startswith("Avery 5160"):
                    pdf_path = run_dir / "qrcc_avery_5160.pdf"
                    save_qr_pdf_avery_5160(pngs, labels, pdf_path)
                else:
                    pdf_path = run_dir / "qrcc_labels.pdf"
                    save_qr_pdf_sheet(pngs, labels, pdf_path)

            code128_path = None
            if self.make_code128.get():
                code128_path = run_dir / "code128_labels.pdf"
                save_code128_pdf_sheet(payloads, labels, code128_path)

            msg_lines = [
                f"Lines: {len(lines)}",
                f"Lines per QR: {int(self.lines_per_qr.get() or 1)}",
                f"QR PNGs: {len(pngs)} file(s)",
                f"Folder: {run_dir}",
            ]
            if pdf_path:
                msg_lines.append(f"QR PDF: {pdf_path.name}")
            if code128_path:
                msg_lines.append(f"1D PDF: {code128_path.name}")

            self.status.config(text="   |   ".join(msg_lines))

            try:
                safe_open_path(run_dir)
            except Exception:
                pass

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    App().mainloop()
