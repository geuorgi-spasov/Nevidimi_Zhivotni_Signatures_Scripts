"""Pytest configuration: put the project root on sys.path."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
