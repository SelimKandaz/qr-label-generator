from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from qr_label_generator import safe_filename, read_assets

def test_safe_filename():
    assert safe_filename("Server 01/A") == "Server_01_A"

def test_read_assets():
    rows = read_assets(ROOT / "examples" / "assets.csv")
    assert len(rows) == 2
    assert rows[0]["asset_id"] == "DEMO-001"
