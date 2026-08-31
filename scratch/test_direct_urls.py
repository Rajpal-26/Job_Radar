import requests
import re
import urllib.parse

def test_direct_google_search_link(name="Mayank Pratap", company="Supersourcing"):
    # When user clicks, what URL takes them directly to LinkedIn profile without login?
    # 1. Google search direct:
    g_query = f'site:linkedin.com/in/ "{name}" "{company}"'
    g_url = f"https://www.google.com/search?q={urllib.parse.quote(g_query)}"
    print("Google Search URL:", g_url)
    
    # 2. Direct name slug:
    # Most LinkedIn profiles use firstname-lastname or similar slug
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')
    direct_in_url = f"https://www.linkedin.com/in/{slug}"
    print("Direct Profile URL:", direct_in_url)
    
    # 3. Public LinkedIn directory search or Google "I'm Feeling Lucky" redirect
    lucky_url = f"https://www.google.com/search?q={urllib.parse.quote(g_query)}&btnI=1"
    print("Google Lucky URL:", lucky_url)

if __name__ == "__main__":
    test_direct_google_search_link()
