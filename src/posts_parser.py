from playwright.sync_api import sync_playwright
import json
import re

url = "https://ok.ru/dk?st.cmd=searchResult&st.mode=Content&st.query=чай"
n = 5
with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        locale="ru-RU"
    )

    cookies = json.load(open("ok_cookies.json", encoding="utf-8"))
    context.add_cookies(cookies)

    page = context.new_page()
    page.goto(url, wait_until="networkidle", timeout=60000)

    for i in range(1, n * 3 + 1):
        page.wait_for_timeout(2000)
        page.mouse.wheel(0, 1000)

    page.wait_for_timeout(5000)

    html = page.content()

    with open("ok_search.html", "w", encoding="utf-8") as f:
        f.write(html)

    pattern = re.compile(
        r'<a\b(?=[^>]*\bclass="[^"]*\bmedia-text_a\b[^"]*")'
        r'(?=[^>]*\baria-label="Открыть топик")'
        r'[^>]*\bhref="([^"]+)"',
        re.IGNORECASE | re.DOTALL
    )

    links = pattern.findall(html)
    print("Найдено ссылок:", len(links))
    for l in links[:5]:
        print(l)

    for i in range(0, n):
        page = context.new_page()
        page.goto(f'https://ok.ru{links[i]}', wait_until="networkidle", timeout=60000)
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
        print(group_name)
        print(date)
        print(text)
        print(likes)
        print(comments)
        print(shared)

    browser.close()
