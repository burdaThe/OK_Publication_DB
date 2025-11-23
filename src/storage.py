import json
from typing import List, Dict


def save_json(page_content: List[Dict], filepath: str) -> None:
    with open(filepath, "w", encoding="utf8") as outfile:
        json.dump(page_content, outfile, indent=4, ensure_ascii=False)
