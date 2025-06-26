from bs4 import BeautifulSoup
import html, codecs
from utils.price import obtener_precio

class PerfumeParser:
    @staticmethod
    def parse(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        script = soup.find('script', type='text/template').text
        script = script.replace('\\n', '').replace('\\t', '').replace('\\"', '"').replace('\"', '"').replace('\\/', '/')
        script = codecs.decode(script, 'unicode_escape')
        cleaned_html = html.unescape(script)
        soup = BeautifulSoup(cleaned_html, 'html.parser')
        
        # Obtener imágenes y filtrar duplicados
        imagenes_raw = [img['src'] for img in soup.find_all('img', class_='img-responsive') if '150x150' not in img['src']]
        imagenes_fuente = list(dict.fromkeys(imagenes_raw))  # Elimina duplicados manteniendo orden

        perfume = {
            'id': soup.find('button', class_='single_add_to_cart_button')['value'] if soup.find('button', class_='single_add_to_cart_button') else 'Sin ID',
            'titulo': soup.find('h2', class_='product_title entry-title show-product-nav').text if soup.find('h2', class_='product_title entry-title show-product-nav') else 'Sin título',
            'precio_actual': obtener_precio(soup.find_all('span', class_='woocommerce-Price-amount amount')[0].text) if soup.find_all('span', class_='woocommerce-Price-amount amount') else 'No price',
            'precio_anterior': obtener_precio(soup.find_all('span', class_='woocommerce-Price-amount amount')[1].text) if len(soup.find_all('span', class_='woocommerce-Price-amount amount')) > 1 else '',
            'descripcion': soup.find('div', id='tab-description').text.replace('Descripción', '') if soup.find('div', id='tab-description') else 'Sin descripción',
            'imagenes_fuente': imagenes_fuente,
            'imagenes': [f'imagen-{i+1}' for i in range(len(imagenes_fuente))]
        }

        return perfume
