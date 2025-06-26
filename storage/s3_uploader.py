import boto3
import requests
from config.settings import ENV_BUCKET_NAME
from utils.mime import get_content_type

class S3Uploader:
    @staticmethod
    def upload_images(data):
        s3 = boto3.client('s3')
        for item in data:
            index = 1
            for image_url in item['imagenes_fuente']:
                image_data = requests.get(image_url).content
                image_name = image_url.split('/')[-1]
                s3_key = f"{item['id']}/imagen-{index}"
                content_type = get_content_type(image_name)
                s3.put_object(Bucket=ENV_BUCKET_NAME, Key=s3_key, Body=image_data, ContentType=content_type)
                index += 1
                print(f"> Imagen subida: {s3_key} ({content_type})")
        
        print("Todas las imágenes han sido subidas a S3, al bucket:", ENV_BUCKET_NAME)

