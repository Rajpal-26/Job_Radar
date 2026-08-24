from playwright.sync_api import sync_playwright

url = "https://in.indeed.com/jobs?q=associate+software+engineer&l=Bengaluru%2C+Karnataka&fromage=10&sort=date"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url)
    page.wait_for_timeout(3000)

    cards = page.query_selector_all("div.cardOutline, div.job_seen_beacon, td.resultContent")
    print(f"Total cards: {len(cards)}")
    for idx, card in enumerate(cards[:3]):
        print(f"\n--- CARD {idx+1} ---")
        title_el = card.query_selector("h2.jobTitle a, a[class*='JobTitle'], h2 a, a.jcs-JobTitle")
        title = title_el.inner_text().strip() if title_el else "NO TITLE"
        href = title_el.get_attribute("href") if title_el else "NO HREF"

        comp_el = card.query_selector("span[data-testid='company-name'], span.companyName, [class*='companyName']")
        company = comp_el.inner_text().strip() if comp_el else "NO COMPANY"

        loc_el = card.query_selector("[data-testid='text-location'], div.companyLocation, [class*='location']")
        location = loc_el.inner_text().strip() if loc_el else "NO LOCATION"

        date_el = card.query_selector("[data-testid='myJobsStateDate'], span.date, [class*='date']")
        date_txt = date_el.inner_text().strip() if date_el else "NO DATE"

        print("Title:", title)
        print("Href:", href[:60] if href else href)
        print("Company:", company)
        print("Location:", location)
        print("Posted:", date_txt)

    browser.close()
