"""Put the harness root on sys.path so tests can ``import pipeline``."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
