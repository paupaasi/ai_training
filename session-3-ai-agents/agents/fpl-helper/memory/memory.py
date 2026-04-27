"""FPL Memory Store - Local storage for FPL data and user preferences."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

AGENT_DIR = Path(__file__).parent
DATA_DIR = AGENT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


class FPLMemory:
    """Memory store for FPL Helper agent."""

    def __init__(self):
        self.data_dir = DATA_DIR
        self.cache_file = self.data_dir / "fpl_cache.json"
        self.squad_file = self.data_dir / "squad.json"
        self.prefs_file = self.data_dir / "preferences.json"

    def get_fpl_cache(self) -> Dict[str, Any]:
        """Get cached FPL data."""
        if not self.cache_file.exists():
            return {}
        try:
            with open(self.cache_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def cache_fpl_data(self, data: Dict[str, Any]) -> bool:
        """Cache FPL data."""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(data, f)
            return True
        except Exception:
            return False

    def get_squad(self) -> Dict[str, Any]:
        """Get saved squad."""
        if not self.squad_file.exists():
            return {"players": []}
        try:
            with open(self.squad_file, "r") as f:
                return json.load(f)
        except Exception:
            return {"players": []}

    def save_squad(self, squad: Dict[str, Any]) -> Dict[str, Any]:
        """Save squad data."""
        try:
            with open(self.squad_file, "w") as f:
                json.dump(squad, f)
            return {"status": "success", "squad": squad}
        except Exception:
            return {"status": "error", "message": "Failed to save squad"}

    def get_preferences(self) -> Dict[str, Any]:
        """Get user preferences."""
        if not self.prefs_file.exists():
            return {}
        try:
            with open(self.prefs_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_preferences(self, prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Save user preferences."""
        try:
            with open(self.prefs_file, "w") as f:
                json.dump(prefs, f)
            return {"status": "success", "preferences": prefs}
        except Exception:
            return {"status": "error", "message": "Failed to save preferences"}