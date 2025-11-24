from playwright.sync_api import BrowserContext, Page, sync_playwright
import json
from config import Config
from src.errors import InvalidCookiePath, BrowserSetupError, PageCreationError
import os.path


class BrowserManager:
    def __init__(self, config: Config):
        self.config = config
        self.playwright = None
        self.browser = None
        self.context: BrowserContext | None = None

    def setup(self):
        """Initialize browser and context."""
        print('Setting up the browser...')
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.config.headless
            )
            self.context = self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                locale="ru-RU"
            )
        except Exception as e:
            raise BrowserSetupError(f'Failed to setup a browser: {e}')

        print('Successfully set up the browser.')
        return self

    def _load_cookies(self):
        """Load cookies into the context."""
        print('Loading cookies...')
        if not os.path.exists(self.config.cookies_path):
            raise InvalidCookiePath(self.config.cookies_path)

        try:
            with open(self.config.cookies_path, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
        except Exception as e:
            raise InvalidCookiePath(f'Failed to read cookies: {e}')

        try:
            self.context.add_cookies(cookies)
            print('Successfully loaded cookies.')
        except Exception as e:
            raise InvalidCookiePath(f'Failed to load cookies: {e}')

    def create_page(self) -> Page:
        """Create new page."""
        try:
            page = self.context.new_page()
        except Exception as e:
            raise PageCreationError(f'Failed to create a new page: {e}')

        return page

    def close(self) -> None:
        """CLose browser."""
        print('Closing the browser. Good Bye!')
        self.browser.close()

    def __enter__(self):
        return self.setup()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
