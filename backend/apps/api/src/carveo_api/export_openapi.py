import json
from pathlib import Path

from carveo_api.main import app


def main() -> None:
    output = Path(__file__).parents[4] / "contracts" / "openapi.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
