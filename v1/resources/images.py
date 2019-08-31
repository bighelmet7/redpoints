import concurrent.futures
import os

import pandas as pd
from flask import Flask, request
from flask_restful import Resource
from redis import Redis
from simplejson import dumps

from const import status
from const.redis_queue import IMAGES_INFO_ASYNC, BATCH_PREDICT
from exceptions import ImageInfoError
from mlteam.extensions import redis_client, session
from models.images import ImageInfo, BatchImage


class ImagesInfoResource(Resource):
    """
    images_info endpoint.
    """

    def post(self):
        data = request.get_json()
        if data is None:
            return {"error": "Data is not provided"}, status.HTTP_422_UNPROCESSABLE_ENTITY

        filepath = data.get('filepath', '')
        if os.path.exists(filepath):
            result = {}
            with open(filepath, 'r') as file:
                images = pd.read_csv(file, delimiter='\t')
                for image in images.itertuples():
                        image_info = ImageInfo(image.id, url=image.url, session=session)
                        result[image.id] = image_info.to_dict()
            return result, status.HTTP_200_OK

        return {"error": "Invalid input file url"}, status.HTTP_422_UNPROCESSABLE_ENTITY


class ImagesInfoAsyncResource(Resource):
    """
    images_info_async endpoint, is a images_info with concurrency for processing
    images and pushing into a Redis queue.
    """

    def post(self):
        data = request.get_json()
        if data is None:
            return {"error": "Data is not provided"}, status.HTTP_422_UNPROCESSABLE_ENTITY

        filepath = data.get('filepath', '')
        if os.path.exists(filepath):
            result = {}
            with open(filepath, 'r') as file:
                images = pd.read_csv(file, delimiter='\t')
                with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                    future_img = {
                        executor.submit(ImageInfo(img.id, url=img.url, session=session).to_dict): img.id
                        for img in images.itertuples()
                    }
                    for future in concurrent.futures.as_completed(future_img):
                        img_id = future_img[future]
                        redis_client.rpush(
                            IMAGES_INFO_ASYNC,
                            dumps({img_id: future.result()})
                        )
            return {"ok": "Processing Images"}, status.HTTP_200_OK

        return {"error": "Invalid input file url"}, status.HTTP_422_UNPROCESSABLE_ENTITY


class BatchPredictResource(Resource):
    """
    batch_predict endpoint.
    """

    def post(self):
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
                batch_images.resize_batch_images(redis_conn=redis_client)
            return {"ok": "Processing Images"}, status.HTTP_200_OK

        return {"error": "Invalid input file url"}, status.HTTP_422_UNPROCESSABLE_ENTITY
