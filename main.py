import boto3
import os
import json
import codecs
import requests
import html
from bs4 import BeautifulSoup
from dotenv import load_dotenv

"""_summary_
Este script se encarga de extraer información de perfumes desde un sitio web,
almacenar los datos en un archivo JSON y subir las imágenes de los perfumes a un bucket de Amazon S3.

La idea es crear un archivo JSON que contenga los datos de los perfumes, incluyendo su ID, título, precio actual, precio anterior, descripción e imágenes.

Hasta aquí está programado, falta refactorizar y acomodar el código para que sea más limpio y eficiente.

Lo nuevo, es conectar con una base de datos noSQL (MongoDB) y subir los datos a la base de datos.
Incluyendo, el enlace a las imágenes que se subieron a S3.

Esto con el fin de que la base de datos pueda ser consultada desde una API RESTful.
Y poder desplegar los datos en una aplicación web estilo catalógo de perfumes.
"""

load_dotenv()

# Variables de entorno
ENV_REGION = os.getenv('REGION')
ENV_OUTPUT = os.getenv('OUTPUT')
ENV_SITEMAP_URL = os.getenv('SITEMAP_URL')
ENV_BUCKET_NAME = os.getenv('BUCKET_NAME')
ENV_AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
ENV_AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# Sitempap del sitio web fuente de perfumes
XML_SITEMAP_PATH = './sitemaps/most_recent_sitemap.xml'

# Archivo JSON generado en forma de Base de datos
DATAJSON_GENERATED_PATH = './data/perfumes.json'

# Variables de configuración
USE_LOCAL_XML = True
BUILD_NEW_JSON = False
CANTIDAD_MAXIMA_PRODUCTOS = 10


def get_product_urls_from_sitemap(ENV_SITEMAP_URL):
    print(ENV_SITEMAP_URL)
    response = requests.get(ENV_SITEMAP_URL)
    with open(XML_SITEMAP_PATH, 'w', encoding='utf-8') as file:
        file.write(response.text)
    soup = BeautifulSoup(response.text, 'xml')
    urls = [url.loc.text for url in soup.find_all('url')][0:CANTIDAD_MAXIMA_PRODUCTOS]
    return urls

def get_product_urls_from_local_xml(XML_SITEMAP_PATH):
    with open(XML_SITEMAP_PATH, 'r', encoding='utf-8') as file:
        response = file.read()
    soup = BeautifulSoup(response, 'xml')
    urls = [url.loc.text for url in soup.find_all('url')][0:CANTIDAD_MAXIMA_PRODUCTOS]
    return urls

def get_product_urls(ENV_SITEMAP_URL):
    if (USE_LOCAL_XML):
        print('Usando XML local')
        return get_product_urls_from_local_xml(XML_SITEMAP_PATH)
    else:
        print('Usando XML de sitemap')
        return get_product_urls_from_sitemap(ENV_SITEMAP_URL)


def obtener_precio(string_precio):
    # Patrón regex para encontrar el valor del precio
    precio_str = string_precio.replace('₡', '').replace(',', '')
    # Convertir a float si es necesario
    precio = float(precio_str)
    return precio


if (BUILD_NEW_JSON):
    lista_perfumes = [] # Para el archivo JSON
    product_urls = get_product_urls(ENV_SITEMAP_URL)
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


    with open(DATAJSON_GENERATED_PATH, 'w') as f:
        json.dump(lista_perfumes, f, indent=4)

    print(f'Se ha creado el archivo JSON "{DATAJSON_GENERATED_PATH}" con los datos de los perfumes.')








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
with open(DATAJSON_GENERATED_PATH, 'r', encoding='utf-8') as file:
    data = json.load(file)

for item in data:
    item_id = item['id']
    for image_url in item['imagenes']:
        # Descarga la imagen
        response = requests.get(image_url)
        image_data = response.content
        image_name = image_url.split('/')[-1]

        # Obtener el tipo de contenido
        content_type = get_content_type(image_name)

        # Crear la clave de S3 incluyendo el ID como subcarpeta
        s3_key = f"{item_id}/{image_name}"

        # Sube la imagen a S3
        s3.put_object(Bucket=ENV_BUCKET_NAME, Key=s3_key, Body=image_data, ContentType=content_type)

        print(f'Subido {image_name} a {ENV_BUCKET_NAME}')
