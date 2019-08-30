import concurrent.futures
import csv
import os

import pandas as pd
from flask import Flask, request
from redis import Redis
from simplejson import dumps

from const import status
from exceptions import ImageInfoError
from mlteam import create_app
from mlteam.extensions import session
from models import ImageInfo, BatchImage

app = create_app()
with app.app_context():
    redis_conn = Redis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=app.config['REDIS_DB']
    )
MAX_WORKERS = app.config['MAX_WORKERS_CONCURRENCY']

@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def handler_unexpected_error(error):
    return 'Unexpected error\n', status.HTTP_500_INTERNAL_SERVER_ERROR

@app.route('/ping/')
def ping():
    return {"ping": "pong"}, status.HTTP_200_OK

@app.route('/images_info/', methods=["POST"])
def images_info():
    data = request.get_json()
    if data is None:
        return {"error": "Data is not provided"}, status.HTTP_422_UNPROCESSABLE_ENTITY

    filepath = data.get('filepath', '')
    if os.path.exists(filepath):
        result = {}         # This should be an array instead of an dict.
        with open(filepath, 'r') as file:
            images = pd.read_csv(file, delimiter='\t')
            for image in images.itertuples():
                    image_info = ImageInfo(image.id, url=image.url, session=session)
                    result[image.id] = image_info.to_dict()
        return result, status.HTTP_200_OK

    return {"error": "Invalid input file url"}, status.HTTP_422_UNPROCESSABLE_ENTITY

@app.route('/images_info_async/', methods=["POST"])
def images_info_async():
    data = request.get_json()
    if data is None:
        return {"error": "Data is not provided"}, status.HTTP_422_UNPROCESSABLE_ENTITY

    filepath = data.get('filepath', '')
    if os.path.exists(filepath):
        result = {}         # This should be an array instead of an dict.
        with open(filepath, 'r') as file:
            images = pd.read_csv(file, delimiter='\t')
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                future_img = {
                    executor.submit(ImageInfo(img.id, url=img.url, session=session).to_dict): img.id
                    for img in images.itertuples()
                }
                for future in concurrent.futures.as_completed(future_img):
                    img_id = future_img[future]
                    redis_conn.rpush(
                        'queue:images',
                        dumps({img_id: future.result()})
                    )
        return {"ok": "Processing Images"}, status.HTTP_200_OK

    return {"error": "Invalid input file url"}, status.HTTP_422_UNPROCESSABLE_ENTITY

@app.route('/batch_predict/', methods=["POST"])
def batch_size():
    data = request.get_json()
    if data is None:
        return {"error": "Data is not provided"}, status.HTTP_422_UNPROCESSABLE_ENTITY

    filepath = data.get('filepath', '')
    if os.path.exists(filepath):
        batch_size = data.get('batch_size', 0)
        if batch_size == 0:
            # If there is not batch size, all the images are processed.
            return {"ok": "Processing Images"}, status.HTTP_200_OK
        with open(filepath, 'r') as file:
            images = pd.read_csv(file, delimiter='\t')
            batch_images = BatchImage(images=images.itertuples(), batch_size=batch_size, session=session)
            batch_images.resize_batch_images(redis_conn=redis_conn)
        return {"ok": "Processing Images"}, status.HTTP_200_OK

    return {"error": "Invalid input file url"}, status.HTTP_422_UNPROCESSABLE_ENTITY
