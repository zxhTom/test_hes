import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(
            "file://"
            + "/Users/zxhtom/zxh/project/git/test_hes/allure_report/index.html"
        )
        await page.pdf(path="allure-report.pdf", format="A4")
        await browser.close()


asyncio.run(main())
