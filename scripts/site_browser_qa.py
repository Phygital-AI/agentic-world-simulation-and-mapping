#!/usr/bin/env python3
"""Run desktop/mobile browser QA for both interactive figures."""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("site_browser_qa_interactive.py")), run_name="__main__")
