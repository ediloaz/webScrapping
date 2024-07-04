import boto3
import os
import json
import codecs
import requests
import html
from bs4 import BeautifulSoup
from dotenv import load_dotenv

path_to_save_sitemap = './sitemaps/most_recent_sitemap.xml'
sitemap_url = os.getenv('SITEMAP_URL')
bucket_name = os.getenv('bucket_name')
data_file = './data/perfumes.json'

USE_LOCAL_XML = True
CANTIDAD_MAXIMA_PRODUCTOS = 2

BUILD_NEW_JSON = False

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


if (BUILD_NEW_JSON):
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
        # No incuir las que llevan '150x150' en la URL (son miniaturas)
        imagenes = [imagen for imagen in imagenes if '150x150' not in imagen['src']]
        perfume['imagenes'] = [imagen['src'] for imagen in imagenes] if imagenes else 'Sin imágenes'
        
        lista_perfumes.append(perfume)
        print(f'Producto {cont}/{len(product_urls)} procesado.')
        cont += 1


    with open(data_file, 'w') as f:
        json.dump(lista_perfumes, f, indent=4)

    print(f'Se ha creado el archivo JSON "{data_file}" con los datos de los perfumes.')








# Función para obtener el ContentType basado en la extensión del archivo
def get_content_type(file_name):
    if file_name.endswith('.jpg') or file_name.endswith('.jpeg'):
        return 'image/jpeg'
    elif file_name.endswith('.png'):
        return 'image/png'
    elif file_name.endswith('.gif'):
        return 'image/gif'
    return 'image/jpeg'  # Default to JPEG


s3 = boto3.client('s3')



# Prueba de conexión con S3
s3 = boto3.client('s3')
response = s3.list_buckets()
print('Conectado a S3 correctamente ✅')


# Lee el archivo JSON
with open(data_file, 'r', encoding='utf-8') as file:
    data = json.load(file)

for item in data:
    item_id = item['id']
    for image_url in item['imagenes']:
        print(f'Descargando {image_url}...')
        # Descarga la imagen
        response = requests.get(image_url)
        image_data = response.content
        image_name = image_url.split('/')[-1]

        # Obtener el tipo de contenido
        content_type = get_content_type(image_name)

        # Crear la clave de S3 incluyendo el ID como subcarpeta
        s3_key = f"{item_id}/{image_name}"

        # Sube la imagen a S3
        s3.put_object(Bucket=bucket_name, Key=s3_key, Body=image_data, ContentType=content_type)

        print(f'Subido {image_name} a {bucket_name}')