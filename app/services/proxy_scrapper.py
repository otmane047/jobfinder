import requests
from bs4 import BeautifulSoup

def fetch_proxies():
    url = 'https://proxylib.com/free-proxy-list/?limit=25&sort_by=uptime&sort_order=desc&country_code=FR&type=HTTPS&anonymity='
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    proxies = []

    # Locate the table containing the proxies
    table = soup.find('table')
    if not table:
        raise Exception("Proxy table not found on the page.")

    # Extract rows from the table
    rows = table.find_all('tr')[1:11]  # Skip the header row and get the first 10 proxies
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 2:
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            proxy = f"{ip}:{port}"
            proxies.append(proxy)
        else:
            print("Skipping a row due to unexpected structure.")

    return proxies

# Fetch the first 10 proxies
proxies = fetch_proxies()
print(proxies)

