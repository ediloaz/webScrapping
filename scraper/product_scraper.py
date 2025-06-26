import requests

class ProductScraper:
    @staticmethod
    def scrape(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/58.0.3029.110'}
        response = requests.get(url, headers=headers)
        return response.content