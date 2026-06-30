"""Filesystem paths for bundled, sanitized data."""

from __future__ import annotations

from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
POLICIES_DIR = DATA_DIR / "policies"
ORDERS_FILE = DATA_DIR / "orders.json"
