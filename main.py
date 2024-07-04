import os
import json
import codecs
import requests
import html
from bs4 import BeautifulSoup
from dotenv import load_dotenv

path_to_save_sitemap = './sitemaps/most_recent_sitemap.xml'
sitemap_url = os.getenv('SITEMAP_URL')

USE_LOCAL_XML = True
CANTIDAD_MAXIMA_PRODUCTOS = 500

def get_product_urls_from_sitemap(sitemap_url):
    response = requests.get(sitemap_url)
    with open(path_to_save_sitemap, 'w', encoding='utf-8') as file:
        file.write(response.text)
    soup = BeautifulSoup(response.text, 'xml')
    urls = [url.loc.text for url in soup.find_all('url')][0:CANTIDAD_MAXIMA_PRODUCTOS]
    return urls

def get_product_urls_from_local_xml(path_to_save_sitemap):
    with open(path_to_save_sitemap, 'r', encoding='utf-8') as file:
        response = file.read()
    soup = BeautifulSoup(response, 'xml')
    urls = [url.loc.text for url in soup.find_all('url')][0:CANTIDAD_MAXIMA_PRODUCTOS]
    return urls

def get_product_urls(sitemap_url):
    if (USE_LOCAL_XML):
        print('Usando XML local')
        return get_product_urls_from_local_xml(path_to_save_sitemap)
    else:
        print('Usando XML de sitemap')
        return get_product_urls_from_sitemap(sitemap_url)


def obtener_precio(string_precio):
    # Patrón regex para encontrar el valor del precio
    precio_str = string_precio.replace('₡', '').replace(',', '')
    # Convertir a float si es necesario
    precio = float(precio_str)
    return precio



lista_perfumes = [] # Para el archivo JSON
product_urls = get_product_urls(sitemap_url)
print(f'Se encontraron {len(product_urls)} URLs de productos.')

# Open each URL and extract the product information
cont = 1
for url in product_urls:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    script = soup.find('script', type='text/template').text
    # Eliminar las secuencias de escape
    script = script.replace('\\n', '').replace('\\t', '').replace('\\"', '"').replace('\"', '"').replace('\\/', '/')
    script = codecs.decode(script, 'unicode_escape')
    cleaned_html = html.unescape(script)

    # Quitar las comillas alrededor del HTML
    cleaned_html = cleaned_html.replace('<script type="text/template">"', '').replace('"</script>', '')

    # Parsear como HTML con BeautifulSoup
    soup = BeautifulSoup(cleaned_html, 'html.parser')

    perfume = {
        'id': '',
        'titulo': '',
        'precio_actual': '',
        'precio_anterior': '',
        'descripcion': '',
        'imagenes': []
    }

    # ATRIBUTO -> ID
    id = soup.find('button', class_='single_add_to_cart_button')
    perfume['id'] = id['value'] if id else 'Sin ID'

    # ATRIBUTO -> TITULO
    titulo = soup.find('h2', class_='product_title entry-title show-product-nav')
    perfume['titulo'] = titulo.text if titulo else 'Sin título'

    # ATRIBUTO -> PRECIO
    prices = soup.find_all('span', class_='woocommerce-Price-amount amount')
    perfume['precio_actual'] = obtener_precio(prices[0].text) if prices else 'No price'
    if (len(prices) > 1):
        perfume['precio_anterior'] = obtener_precio(prices[1].text) if prices else 'No price'

    # ATRIBUTO -> DESCRIPCIÓN
    descripcion = soup.find('div', id='tab-description')
    perfume['descripcion'] = descripcion.text.replace('Descripción', '') if descripcion else 'Sin descripción'

    # ATRIBUTO -> IMÁGENES
    imagenes = soup.find_all('img', class_='img-responsive')
    perfume['imagenes'] = [imagen['src'] for imagen in imagenes] if imagenes else 'Sin imágenes'
    
    lista_perfumes.append(perfume)
    print(f'Producto {cont}/{len(product_urls)} procesado.')
    cont += 1

nombre_archivo = './data/perfumes.json'
with open(nombre_archivo, 'w') as f:
    json.dump(lista_perfumes, f, indent=4)

print(f'Se ha creado el archivo JSON "{nombre_archivo}" con los datos de los perfumes.')