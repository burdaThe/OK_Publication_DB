from playwright.sync_api import sync_playwright
import json

url = "https://ok.ru/dk?st.cmd=searchResult&st.mode=Content&st.query=чай"

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
    page.wait_for_timeout(5000)

    html = page.content()

    with open("ok_search.html", "w", encoding="utf-8") as f:
        f.write(html)

    browser.close()
