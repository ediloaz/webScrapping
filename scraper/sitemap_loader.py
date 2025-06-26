import requests
from bs4 import BeautifulSoup
from config.settings import XML_SITEMAP_PATH

class SitemapScraper:
    def __init__(self, url, use_local=False, path=XML_SITEMAP_PATH):
        self.url = url
        self.use_local = use_local
        self.path = path

    def get_urls(self, max_count):
        if self.use_local:
            with open(self.path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            response = requests.get(self.url)
            content = response.text
            with open(self.path, 'w', encoding='utf-8') as f:
                f.write(content)

        soup = BeautifulSoup(content, 'xml')
        return [u.loc.text for u in soup.find_all('url')][:max_count]
