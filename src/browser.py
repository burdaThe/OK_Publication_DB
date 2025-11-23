from playwright.sync_api import BrowserContext, Page, sync_playwright
from typing import Optional
import json
from config import Config


class BrowserManager:
    def __init__(self, config: Config):
        self.config = config
        self.playwright = None
        self.browser = None
        self.context: Optional[BrowserContext] = None

    def setup(self):
        """Initialize browser and context."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.config.headless
        )
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            locale="ru-RU"
        )
        # self._load_cookies()

        return self

    def _load_cookies(self):
        """Load cookies into the context."""
        with open(self.config.cookies_path, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        self.context.add_cookies(cookies)

    def create_page(self) -> Page:
        """Create new page."""
        page = self.context.new_page()
        return page

    def close(self) -> None:
        """CLose browser."""
        self.browser.close()

    def __enter__(self):
        return self.setup()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()






