import csv
import os
import concurrent.futures

import pandas as pd
from flask import Flask, request
from redis import Redis
from requests import Session
from const import status
from exceptions import ImageInfoError
from models import ImageInfo

app = Flask(__name__)

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
        session = Session() # Global session for requesting all images
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
        session = Session() # Global session for requesting all images
        with open(filepath, 'r') as file:
            images = pd.read_csv(file, delimiter='\t')
            # TODO: avoid harded values, max_workers.
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                future_img = {
                    executor.submit(ImageInfo(img.id, url=img.url, session=session).to_dict): img.id
                    for img in images.itertuples()
                }
                for future in concurrent.futures.as_completed(future_img):
                    img_id = future_img[future]
                    result[img_id] = future.result()
        return result, status.HTTP_200_OK

    return {"error": "Invalid input file url"}, status.HTTP_422_UNPROCESSABLE_ENTITY