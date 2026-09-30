#!/usr/bin/env python3
"""Deterministically build the interactive bilingual publication."""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("site_builder_interactive.py")), run_name="__main__")
