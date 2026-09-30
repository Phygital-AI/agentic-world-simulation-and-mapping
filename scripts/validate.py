#!/usr/bin/env python3
"""Public entry point for publication validation."""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("site_validator.py")), run_name="__main__")
