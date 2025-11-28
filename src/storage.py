import json
from typing import List, Dict
from src.errors import SaveJsonError


def save_json(page_content: List[Dict], filepath: str) -> None:
    try:
        print(f'Saving JSON with posts content.')
        with open(filepath, "w", encoding="utf8") as outfile:
            json.dump(page_content, outfile, indent=4, ensure_ascii=False)
        print('Successfully saved JSON.')

    except Exception as e:
        raise SaveJsonError(f'Failed to save JSON: {e}')
