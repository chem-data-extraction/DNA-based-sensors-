#!/usr/bin/env python3
"""
Runs the two-step web pipeline:
1) scripts/extract_web_candidates.py
2) scripts/select_web_records.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script: str) -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / script)], check=True)


def main() -> None:
    run("extract_web_candidates.py")
    run("select_web_records.py")


if __name__ == "__main__":
    main()
