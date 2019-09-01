from io import BytesIO
from collections import namedtuple
from unittest.mock import patch
from unittest import TestCase

import numpy as np
import requests_mock
from PIL import Image, ImageFile
from PIL.GifImagePlugin import GifImageFile
from requests.exceptions import ReadTimeout
from redis import Redis
from simplejson import loads

from const.redis_queue import BATCH_PREDICT
from exceptions import ImageInfoError
from mlteam.extensions import session
from models.images import ImageInfo, BatchImage

# ISSUE: https://github.com/python-pillow/Pillow/issues/1510
ImageFile.LOAD_TRUNCATED_IMAGES = True


class ImageInfoTest(TestCase):

    def setUp(self):
        self.session = session
        self.blank_image_64_64 = Image.new('RGB', (64, 64))
        with BytesIO () as output:
            self.blank_image_64_64.save(output, format="GIF")
            self.img_buf = output.getvalue()

    def test_get_image_valid(self):
        url = "https://www.url.com/blank_image_64_64"
        img = ImageInfo(id=0, url=url)
        with requests_mock.mock() as m:
            m.get(url, content=self.img_buf)
            img_response = img._get_image()
            # img_response should be the same size as the blank 64x64 image.
            self.assertEqual(img_response.size, self.blank_image_64_64.size)

    def test_get_image_returns_pil_image_object(self):
        url = "https://www.url.com/blank_image_64_64"
        img = ImageInfo(id=0, url=url)
        with requests_mock.mock() as m:
            m.get(url, content=self.img_buf)
            img_response = img._get_image()
            # img_response must be a PIL valid image object
            self.assertEqual(type(img_response), GifImageFile)

    def test_get_image_could_not_be_opened(self):
        url = "https://www.url.com/blank_image_64_64"
        img = ImageInfo(id=0, url=url)
        with requests_mock.mock() as m:
            m.get(url, content=b'')
            # The requests returns an empty content.
            with self.assertRaises(ImageInfoError):
                img_response = img._get_image()

    def test_get_image_could_not_be_requested(self):
        url = "https://www.url.com/blank_image_64_64"
        img = ImageInfo(id=0, url=url)
        with requests_mock.mock() as m:
            m.get(url, content=b'', status_code=404)
            # The requests with status not OK raises an exception.
            with self.assertRaises(ImageInfoError):
                img_response = img._get_image()

    def test_resize_an_image(self):
        url = "https://www.url.com/blank_image_64_64"
        img = ImageInfo(id=0, url=url)
        blank = Image.new('RGB', (80, 80))
        # Resizes an image of 64x64 to 80x80.
        with patch('models.images.ImageInfo._get_image', return_value=self.blank_image_64_64):
            pixels, _ = img.resize(80, 80)
            expected_pixels = np.array(blank)
            self.assertTrue(np.array_equal(pixels, expected_pixels.tolist()))

    def test_resize_an_image_with_an_invalid_image(self):
        url = "https://www.url.com/blank_image_64_64"
        img = ImageInfo(id=0, url=url)
        with requests_mock.mock() as m:
            m.get(url, content=b'')
            # The requests will return an empty content, raising an
            # ImageInfoError.
            pixels, _ = img.resize(80, 80)
            expected_pixels = np.zeros(1).tolist()
            self.assertTrue(np.array_equal(pixels, expected_pixels))

    def test_to_dict(self):
        url = "https://www.url.com/blank_image_64_64"
        img = ImageInfo(id=0, url=url)
        blank = Image.new('RGB', (64, 64))
        # This is necessary for giving a format to our blank image.
        with BytesIO () as output:
            blank.save(output, format="GIF")
            img_buf = output.getvalue()
            blank_gif = Image.open(BytesIO(img_buf))
        with requests_mock.mock() as m:
            m.get(url, content=self.img_buf)
            result = img.to_dict()
            expected = {
                "url": url,
                "image_info": {
                    "image_size": len(img_buf),
                    "image_dimension": blank_gif.size,
                    "image_format": blank_gif.format,
                }
            }
            self.assertEqual(result, expected)

    def test_to_dict_could_not_open_the_image(self):
        url = "https://www.url.com/blank_image_64_64"
        img = ImageInfo(id=0, url=url)
        with requests_mock.mock() as m:
            m.get(url, content=b'')
            result = img.to_dict()
            expected = {
                "url": url,
                "image_info": '',
                "error": "Image could not be opened."
            }
            self.assertEqual(result, expected)

    def test_to_dict_could_not_be_requested_the_image(self):
        url = "https://www.url.com/blank_image_64_64"
        img = ImageInfo(id=0, url=url)
        with requests_mock.mock() as m:
            m.get(url, content=b'', status_code=404)
            result = img.to_dict()
            expected = {
                "url": url,
                "image_info": '',
                "error": "Image could not be requested."
            }
            self.assertEqual(result, expected)

    def tearDown(self):
        self.blank_image_64_64.close()


class BatchImageTest(TestCase):

    def setUp(self):
        ImageInfoTSV = namedtuple('ImageInfoTSV', ['id', 'url'])
        self.images = [
            ImageInfoTSV(id=0, url="https://www.url.com/blank_image"),
        ]
        self.session = session
        # Redis testing propouse.
        self.redis_client = Redis(host='localhost', port=6379, db=0)

    def test_send_to_redis_queue_valid_connection(self):
        batch_images = BatchImage(
            batch_size=2,
        )
        blank_image_64_64 = Image.new('RGB', (64,64))
        images = [
            np.array(blank_image_64_64).tolist()
        ]
        n_channels = 3
        queue = 'queue:tst-batch-predict'
        batch_images._send_to_redis_queue(n_channels, 64, 64, images, self.redis_client, queue)
        result_str = self.redis_client.rpop(queue)
        result = loads(result_str)
        expected_batch_dimension = '({batch_size}, {ch}, {x}, {y})'.format(
            batch_size=batch_images.batch_size,
            ch=n_channels,
            x=64,
            y=64
        )
        expected = {
            'batch_dimension': expected_batch_dimension,
            'images': list(images)
        }
        self.assertEqual(result, expected)

    def test_resize_batch_images(self):
        batch_images = BatchImage(
            images=self.images,
            batch_size=2,
        )
        queue = 'queue:tst-batch-predict'
        blank = Image.new('RGB', (80, 80))
        # This is necessary for giving a format to our blank image.
        with BytesIO () as output:
            blank.save(output, format="GIF")
            img_buf = output.getvalue()
        with requests_mock.mock() as m:
            m.get('https://www.url.com/blank_image', content=img_buf)
            batch_images.resize_batch_images(redis_conn=self.redis_client, queue=queue)
            result_str = self.redis_client.rpop(queue)
            result = loads(result_str)
            # The new sizes of the previous image 80x80.
            expected = (64,64,)
            self.assertEqual(np.shape(result['images'][0]), expected)

    def tearDown(self):
        self.redis_client.flushdb()
