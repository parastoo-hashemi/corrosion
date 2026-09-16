"""Expose the repository path mapper to standalone report scripts."""
from pathlib import Path
import sys

PARENT = Path(__file__).resolve().parents[3]
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

from corrosion.research_paths import resolve_project_path
