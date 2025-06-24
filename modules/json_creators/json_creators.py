import boto3
import os
import json
import codecs
import requests
import html
from bs4 import BeautifulSoup
from dotenv import load_dotenv

data_file = './data/perfumes.json'
data_without_images_file = './data/perfumes_without_images.json'

# returns the same json file without images, deletes the images key
def create_json_without_images(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    for item in data:
        del item['imagenes']
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f'Se ha creado el archivo JSON "{file_path}" sin las imágenes.') 

# returns the same json file without images, deletes the images key. In a new file
def create_json_without_images(file_path, file_without_images_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for perfume in data:
            del perfume['images']
        with open(file_without_images_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    print(f'File {file_without_images_path} created successfully.')
    

# returns new json file with the images string BUT the string only the last part of the url,
# for example
# from: "https://WEBSITE.COM/wp-content/uploads/2019/11/61949216-01.jpg" to: "61949216-01.jpg"
def create_json_with_images_names_only(file_path, new_file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for perfume in data:
            perfume['imagenes'] = [image_url.split('/')[-1] for image_url in perfume['imagenes']]
        with open(new_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    print(f'File {new_file_path} created successfully.')

create_json_with_images_names_only(data_file, './data/perfumes_images_names_only.json')
