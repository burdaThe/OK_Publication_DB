from playwright.sync_api import BrowserContext
import json
import time
from config import Config


class Authentication:
    def __init__(self, config: Config):
        self.config = config

    def create_cookies(self, context: BrowserContext) -> None:
        """Create cookies. User needs to log in."""

        page = context.new_page()
        page.goto('https://ok.ru/')

        time.sleep(30)

        cookies = context.cookies()
        if not cookies:
            raise Exception("Couldn't get cookies after authentication.")

        with open(self.config.cookies_path, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
