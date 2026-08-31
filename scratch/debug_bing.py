import requests
import lxml.html
import urllib.parse

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
query = 'site:linkedin.com/in/ "Razorpay" "Recruiter"'
url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
r = requests.get(url, headers=headers)
doc = lxml.html.fromstring(r.text)

for item in doc.xpath('//li[contains(@class, "b_algo")]'):
    title = item.xpath('.//h2/a')[0].text_content()
    href = item.xpath('.//h2/a')[0].get("href")
    print(title)
    print(href)
    print()
