from typing import Dict
from playwright.sync_api import Page, BrowserContext
from config import Config
from src.errors import SearchError, ParsePostError
import re


class PostParser:
    def __init__(self, config: Config):
        self.config = config

    def extract_links(self, page: Page):
        """Extract post links."""

        links = set()
        page.goto(self.config.search_url)

        while True:
            if len(links) >= self.config.n_posts:
                return list(links)[:self.config.n_posts]
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)

            html = page.content()

            with open("ok_search.html", "w", encoding="utf-8") as f:
                f.write(html)

            pattern = re.compile(
                r'<a\b(?=[^>]*\bclass="[^"]*\bmedia-text_a\b[^"]*")'
                r'(?=[^>]*\baria-label="Открыть топик")'
                r'[^>]*\bhref="([^"]+)"',
                re.IGNORECASE | re.DOTALL
            )

            links_scroll = pattern.findall(html)

            for link in links_scroll:
                links.add(link)
                if len(links) >= self.config.n_posts:
                    return list(links)[:self.config.n_posts]

            if len(links) == 0:
                raise SearchError('Search error. Found 0 posts. Search target might be too specific.')

    @staticmethod
    def parse_post(link: str, context: BrowserContext) -> str:
        """Extract post HTML."""
        page = context.new_page()
        page.goto(f'{'https://ok.ru'}{link}', wait_until="networkidle", timeout=60000)
        post_html = page.content()

        if len(post_html) == 0:
            raise ParsePostError('https://ok.ru' + link)

        return post_html

    @staticmethod
    def extract_data(post_html: str, link: str) -> Dict:
        """Extract data from post."""
        group_name_pattern = re.compile(
            r'<div\s+class="group-name__63bs8"\s*>(.*?)</div>',
            re.DOTALL | re.IGNORECASE
        )
        group_name = group_name_pattern.findall(post_html)

        date_pattern = re.compile(
            r'<time[^>]*>(.*?)</time>',
            re.DOTALL | re.IGNORECASE
        )
        date = date_pattern.findall(post_html)

        block_pattern = re.compile(
            r'<div[^>]*class="media-text_cnt_tx[^"]*"[^>]*>(.*?)</div>',
            re.DOTALL | re.IGNORECASE
        )
        blocks = block_pattern.findall(post_html)
        texts = []

        for block in blocks:
            block = re.sub(r'<img[^>]*>', '', block)
            block = re.sub(r'<[^>]+>', '', block)
            clean = block.strip()

            if clean:
                texts.append(clean)

        clean_lines = []
        for t in texts:
            for line in t.split("\n"):
                line = line.strip()
                if line:
                    clean_lines.append(line)

        text = ". ".join(clean_lines)

        likes_pattern = re.compile(
            r'<span[^>]*data-msg="reactedWithCount"[^>]*>(.*?)</span>',
            re.IGNORECASE | re.DOTALL
        )
        likes_matches = likes_pattern.findall(post_html)
        if likes_matches:
            m = re.search(r'\d+', likes_matches[0])
            likes = int(m.group(0)) if m else 0
        else:
            likes = 0

        comments_pattern = re.compile(
            r'<span[^>]*class="[^"]*\blstp-t\b[^"]*\bcomments-counter\b[^"]*"[^>]*>(.*?)</span>',
            re.IGNORECASE | re.DOTALL
        )
        m = comments_pattern.findall(post_html)
        comments = int(re.search(r'\d+', m[0]).group(0)) if m else 0
        shared_pattern = re.compile(
            r'<span[^>]*data-parent-class="feed_info_sm"[^>]*>(.*?)</span>',
            re.IGNORECASE | re.DOTALL
        )
        shared_matches = shared_pattern.findall(post_html)
        if shared_matches:
            num_match = re.search(r'\d+', shared_matches[0])
            shared = int(num_match.group(0)) if num_match else 0
        else:
            shared = 0

        page_content = {
            "link": link,
            "group_name": group_name[0],
            "date": date[0],
            "text": text,
            "num_likes": likes,
            "num_comments": comments,
            "num_shared": shared
        }

        str_content = ['link', 'group_name', 'date']
        for key, value in page_content:
            if key in str_content:
                if len(value) == 0:
                    print(f'Warning! Unknown behavior for {key} in https://ok.ru{link}')

        return page_content
