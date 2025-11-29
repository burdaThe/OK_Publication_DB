import os.path
from config import Config
from src.browser import BrowserManager
from src.parser import PostParser
from src.storage import save_json
from src.auth import Authentication


def main():

    # указание ключевого слова, количества постов

    config = Config('ключевое_слово', 7, False)
    with BrowserManager(config) as browser:

        if not os.path.exists('ok_cookies.json'):
            auth = Authentication(config)
            auth.create_cookies(browser.context)

        browser.load_cookies()

        page = browser.create_page()
        parser = PostParser(config)
        links = parser.extract_links(page)

        content = []
        for link in links:
            post_html = parser.parse_post(link, browser.context)
            content.append(parser.extract_data(post_html, link, config))

        print(f'Parsed {len(links)} posts. Saved to {config.output_path}')

        save_json(content, config.output_path)


if __name__ == '__main__':
    main()
