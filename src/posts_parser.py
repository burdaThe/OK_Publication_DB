from playwright.sync_api import sync_playwright
import json
import re
import time

n = 5
SEARCH_TARGET = 'чай'

MAIN_DOMEN_URL = 'https://ok.ru'
URL = f'{MAIN_DOMEN_URL}/dk?st.cmd=searchResult&st.mode=Content&st.query={SEARCH_TARGET}'

def save_json(data, name = "output.json"):
    with open(name, "w", encoding="utf8") as outfile:
        json.dump(data, outfile, indent=4, ensure_ascii=False)

def link_data_retrieve(link, context):
    try:
        page = context.new_page()
        page.goto(f'{MAIN_DOMEN_URL}{link}', wait_until="networkidle", timeout=60000)
        post_html = page.content()

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

        text = "\n".join(clean_lines)

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
        return page_content
    except Exception as e:
        print(f"Extracting data from page error: {e}")

def get_links_from_page(page):
    links = []
    while len(links) < n:
        page.wait_for_timeout(800)
        page.mouse.wheel(0, 1000)
        page.wait_for_timeout(200)

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
        for i in links_scroll:
            links.append(i)

    return links

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            locale="ru-RU"
        )
        try:
            cookies = json.load(open("ok_cookies.json", encoding="utf-8"))
            context.add_cookies(cookies)

            page = context.new_page()
            page.goto(URL, wait_until="networkidle", timeout=60000)

            links = get_links_from_page(page)
            content = []

            for i in range(0, n):
                print(links[i])
                page_content=link_data_retrieve(links[i], context)
                print(page_content)
                content.append(page_content)

            browser.close()
            save_json(content)
        except KeyboardInterrupt:
            print(f"Query was interrupted. Closing browser")
            browser.close()
        except FileNotFoundError as e:
            print(f"Not found file: {e.filename}")
        except Exception as e:
            print(f"Unknown error in main: {e}")

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(f"Time for the query: {end-start:.2f} seconds")