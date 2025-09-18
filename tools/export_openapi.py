import json
import sys
from pathlib import Path

from app.main import app

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

spec = app.openapi()
Path("openapi.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
print("Wrote openapi.json")
