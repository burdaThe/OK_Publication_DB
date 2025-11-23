import os.path
import sys
from typing import List, Dict
from config import Config
from src.browser import BrowserManager
from src.parser import PostParser
from src.storage import save_json
from src.auth import Authentication


def main():
    config = Config('Чай', 5, False)
    with BrowserManager(config) as browser:
        if not os.path.exists('ok_cookies.json'):
            auth = Authentication(config)
            auth.create_cookies(browser.context)

        browser._load_cookies()

        page = browser.create_page()
        parser = PostParser(config)
        links = parser.extract_links(page)
        print(len(links), sep='\n')
        content = []
        for link in links:
            post_html = parser.parse_post(link, browser.context)
            content.append(parser.extract_data(post_html, link))

        print(len(content), content[0])

        save_json(content, 'content.json')


if __name__ == '__main__':
    main()





