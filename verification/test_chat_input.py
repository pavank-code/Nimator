from playwright.sync_api import Page, expect, sync_playwright

def test_tutor_page(page: Page):
    # Navigate to Tutor page
    page.goto("http://localhost:3000/tutor")

    # Wait for the input area to be visible
    # The textarea has a placeholder "Ask about math..."
    textarea = page.get_by_placeholder("Ask about math, physics, algorithms, or ML...")
    expect(textarea).to_be_visible()

    # Type something to ensure it works (controlled component)
    textarea.fill("Hello World")
    expect(textarea).to_have_value("Hello World")

    # Take a screenshot
    page.screenshot(path="verification/tutor_page.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            test_tutor_page(page)
        finally:
            browser.close()
