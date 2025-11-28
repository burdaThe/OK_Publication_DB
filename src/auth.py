from playwright.sync_api import BrowserContext
from src.errors import CookiesSaveError
import json
from config import Config


class Authentication:
    def __init__(self, config: Config):
        self.config = config

    def create_cookies(self, context: BrowserContext) -> None:
        """Create cookies. User needs to log in."""
        print('Log in your account and close the browser.')
        page = context.new_page()
        page.goto('https://ok.ru/')

        page.wait_for_event("close", timeout=6000000)

        cookies = context.cookies()
        if not cookies:
            raise Exception("Couldn't get cookies after authentication.")

        try:
            with open(self.config.cookies_path, "w", encoding="utf-8") as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise CookiesSaveError(f'Failed to save cookies to {self.config.cookies_path}. {e}')
