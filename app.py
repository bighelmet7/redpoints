import csv
import os
from collections import namedtuple

from flask import Flask, request
from requests import Session
from const import status
from exceptions import ImageInfoError
from models import ImageInfo

app = Flask(__name__)

@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def handler_unexpected_error(error):
    return 'Unexpected error\n'

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
            ImageTSV = namedtuple('ImageTSV', ['id', 'url'])
            images = map(ImageTSV._make, csv.reader(file, delimiter='\t'))
            for image in images:
                try:
                    image_info = ImageInfo(image.id, url=image.url, session=session).to_dict()
                    result[image.id] = {
                        "url": image.url, 
                        "image_info": image_info
                    }
                except ImageInfoError as e:
                    result[image.id] = {
                        "url": image.url, 
                        "image_info": '',
                        "error": str(e)
                    }
        return result, status.HTTP_200_OK

    return {"error": "Invalid input file url"}, status.HTTP_422_UNPROCESSABLE_ENTITY

@app.route('/images_info_async/', methods=["POST"])
def images_info_async():
    pass