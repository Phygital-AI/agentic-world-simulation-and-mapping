#!/usr/bin/env python3
"""Public entry point for optional browser QA."""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("site_browser_qa.py")), run_name="__main__")
