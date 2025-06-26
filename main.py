import html

from config.settings import ENV_SITEMAP_URL, CANTIDAD_MAXIMA_PRODUCTOS
from scraper.sitemap_loader import SitemapScraper
from scraper.product_scraper import ProductScraper
from parser.perfume_parser import PerfumeParser
from storage.json_writer import JSONWriter
from storage.s3_uploader import S3Uploader

print("Iniciando proceso de scraping de perfumes...")

scraper = SitemapScraper(url=ENV_SITEMAP_URL)
urls = scraper.get_urls(max_count=CANTIDAD_MAXIMA_PRODUCTOS)

print()
print(f"URLs a procesar: {len(urls)}")

perfumes = []
for i, url in enumerate(urls, 1):
    html = ProductScraper.scrape(url)
    perfume = PerfumeParser.parse(html)
    perfumes.append(perfume)
    print(f"[{i}/{len(urls)}] Procesado: {perfume['id']} - {perfume['titulo']}")

JSONWriter.write(perfumes)
S3Uploader.upload_images(perfumes)

print()
print("Proceso finalizado ✅")