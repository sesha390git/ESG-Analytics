"""Open the Streamlit Community Cloud app in a headless browser and wake it if asleep.

A plain curl/HTTP GET isn't enough: a sleeping app serves a page with a
"Yes, get this app back up!" button that has to be clicked. A real browser
session also counts as genuine traffic, which keeps an awake app from sleeping.
"""

import os
import sys

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

WAKE_BUTTON_TEXT = "Yes, get this app back up"


def main() -> int:
    url = os.environ.get("STREAMLIT_APP_URL")
    if not url:
        print("STREAMLIT_APP_URL is not set (see the workflow's env block).")
        return 1

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60_000)

        wake_button = page.get_by_role("button", name=WAKE_BUTTON_TEXT)
        try:
            wake_button.wait_for(state="visible", timeout=15_000)
            print("App is asleep - clicking the wake button.")
            wake_button.click()
            # Waking takes a while; wait for the button to go away.
            wake_button.wait_for(state="detached", timeout=180_000)
            print("Wake requested; app is booting.")
        except PlaywrightTimeout:
            print("No wake button found - app is already awake.")

        # Hang around briefly so the visit registers as a real session.
        page.wait_for_timeout(10_000)
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
