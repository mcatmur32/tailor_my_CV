import asyncio
from playwright.async_api import async_playwright
import base64
from openai import OpenAI

# ======================
# CONFIG
# ======================
BRIGHT_URL = "https://www.brightnetwork.co.uk/graduate-jobs/"
OUTPUT_SCREENSHOT = "bright_jobs.png"
OPENAI_MODEL = "gpt-4o-mini"  # fast + vision
client = OpenAI()

# ======================
# MAIN FUNCTION
# ======================
async def scrape_bright_jobs():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("🌍 Navigating to Bright Network...")
        await page.goto(BRIGHT_URL, timeout=60000)

        # Try to wait for job cards
        try:
            await page.wait_for_selector(".opportunity-card", timeout=10000)
            print("✅ Found job cards on page!")

            jobs = await page.query_selector_all(".opportunity-card")

            job_list = []
            for job in jobs[:10]:  # limit to 10
                title_el = await job.query_selector("h3")
                company_el = await job.query_selector(".opportunity-card__organisation")
                link_el = await job.query_selector("a")

                title = await title_el.inner_text() if title_el else "N/A"
                company = await company_el.inner_text() if company_el else "N/A"
                link = await link_el.get_attribute("href") if link_el else None

                job_list.append({
                    "title": title.strip(),
                    "company": company.strip(),
                    "url": f"https://www.brightnetwork.co.uk{link}" if link else None
                })

            await browser.close()
            return job_list

        except Exception as e:
            print(f"⚠️ Failed to scrape directly: {e}")
            print("📸 Taking screenshot for AI parsing...")

            # Take screenshot for AI fallback
            await page.screenshot(path=OUTPUT_SCREENSHOT, full_page=True)
            await browser.close()

            with open(OUTPUT_SCREENSHOT, "rb") as img:
                img_base64 = base64.b64encode(img.read()).decode("utf-8")

                response = client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an assistant that extracts job listings."},
                        {"role": "user", "content": [
                            {"type": "text", "text": "Extract the first 10 job listings (title, company, URL if visible) from this screenshot. Return JSON."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                        ]}
                    ]
                )

            ai_jobs = response.choices[0].message.content
            return ai_jobs

# ======================
# RUN
# ======================
if __name__ == "__main__":
    jobs = asyncio.run(scrape_bright_jobs())
    print("\n=== JOBS FOUND ===")
    print(jobs)
