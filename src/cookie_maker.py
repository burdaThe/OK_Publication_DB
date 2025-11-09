from playwright.sync_api import sync_playwright
import json
import time

url = "https://ok.ru/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        locale="ru-RU"
    )

    page = context.new_page()
    page.goto(url)

    time.sleep(60)

    cookies = context.cookies()
    with open("ok_cookies.json", "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)
    print("Куки сохранены в ok_cookies.json")

    browser.close()