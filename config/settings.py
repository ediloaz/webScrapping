import os
from dotenv import load_dotenv

load_dotenv()

ENV_SITEMAP_URL = os.getenv('SITEMAP_URL')
ENV_BUCKET_NAME = os.getenv('BUCKET_NAME')
CANTIDAD_MAXIMA_PRODUCTOS = 4
REGION = os.getenv('REGION')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
DATAJSON_GENERATED_PATH = './data/perfumes.json'
XML_SITEMAP_PATH = './sitemaps/most_recent_sitemap.xml'