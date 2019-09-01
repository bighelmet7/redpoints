from io import BytesIO
from unittest.mock import mock_open, patch
from unittest import TestCase

import requests_mock
from PIL import Image
from simplejson import loads

from mlteam import create_app


class ImagesInfoResourceTest(TestCase):

    def setUp(self):
        self.app = create_app(config_obj='mlteam.config.TestingConfig')

    def test_status_ok(self):
        data = {'filepath': '/redpoints/src/dependencies/images.tsv'}

        images_tsv = "id\turl\n0\thttps://www.url.com/blank_image"
        blank = Image.new('RGB', (64,64))
        img_buf = None
        with BytesIO() as output:
            blank.save(output, format="GIF")
            img_buf = output.getvalue()
            blank_img = Image.open(BytesIO(img_buf))

        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=images_tsv)):
                with requests_mock.mock() as m:
                    with self.app.test_client() as cli:
                        m.get('https://www.url.com/blank_image', content=img_buf)
                        resp = cli.post('/api/v1/images_info/', json=data)
                        expected = {
                            "0": {
                                "url": "https://www.url.com/blank_image",
                                "image_info": {
                                    "image_size": len(img_buf),
                                    "image_dimension": list(blank_img.size),
                                    "image_format": blank_img.format,
                                }
                            }
                        }
                        self.assertEqual(resp.status_code, 200)
                        self.assertEqual(loads(resp.data), expected)

    def test_status_422_data_is_not_provieded(self):
        with self.app.test_client() as cli:
            resp = cli.post('/api/v1/images_info/')
            expected = {
                "error": "Data is not provided"
            }
            self.assertEqual(resp.status_code, 422)
            self.assertEqual(loads(resp.data), expected)

    def test_status_422_filepath_does_not_exists(self):
        data = {'filepath': '/redpoints/src/dependencies/images.tsv'}

        with patch('os.path.exists', return_value=False):
            with self.app.test_client() as cli:
                resp = cli.post('/api/v1/images_info/', json=data)
                expected = {
                    "error": "Invalid input file url"
                }
                self.assertEqual(resp.status_code, 422)
                self.assertEqual(loads(resp.data), expected)


class ImagesInfoAsyncResourceTest(TestCase):

    def setUp(self):
        self.app = create_app(config_obj='mlteam.config.TestingConfig')

    def test_status_ok(self):
        data = {'filepath': '/redpoints/src/dependencies/images.tsv'}

        images_tsv = "id\turl\n0\thttps://www.url.com/blank_image"
        blank = Image.new('RGB', (64,64))
        img_buf = None
        with BytesIO() as output:
            blank.save(output, format="GIF")
            img_buf = output.getvalue()
            blank_img = Image.open(BytesIO(img_buf))

        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=images_tsv)):
                with requests_mock.mock() as m:
                    with self.app.test_client() as cli:
                        m.get('https://www.url.com/blank_image', content=img_buf)
                        resp = cli.post('/api/v1/images_info_async/', json=data)
                        expected = {
                            "ok": "Processing Images"
                        }
                        self.assertEqual(resp.status_code, 200)
                        self.assertEqual(loads(resp.data), expected)

    def test_status_422_data_is_not_provieded(self):
        with self.app.test_client() as cli:
            resp = cli.post('/api/v1/images_info_async/')
            expected = {
                "error": "Data is not provided"
            }
            self.assertEqual(resp.status_code, 422)
            self.assertEqual(loads(resp.data), expected)

    def test_status_422_filepath_does_not_exists(self):
        data = {'filepath': '/redpoints/src/dependencies/images.tsv'}

        with patch('os.path.exists', return_value=False):
            with self.app.test_client() as cli:
                resp = cli.post('/api/v1/images_info_async/', json=data)
                expected = {
                    "error": "Invalid input file url"
                }
                self.assertEqual(resp.status_code, 422)
                self.assertEqual(loads(resp.data), expected)


class BatchPredictResourceTest(TestCase):

    def setUp(self):
        self.app = create_app(config_obj='mlteam.config.TestingConfig')

    def test_status_ok_without_batch_provided(self):
        data = {'filepath': '/redpoints/src/dependencies/images.tsv'}

        images_tsv = "id\turl\n0\thttps://www.url.com/blank_image"
        blank = Image.new('RGB', (64,64))
        img_buf = None
        with BytesIO() as output:
            blank.save(output, format="GIF")
            img_buf = output.getvalue()
            blank_img = Image.open(BytesIO(img_buf))

        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=images_tsv)):
                with requests_mock.mock() as m:
                    with self.app.test_client() as cli:
                        m.get('https://www.url.com/blank_image', content=img_buf)
                        resp = cli.post('/api/v1/batch_predict/', json=data)
                        expected = {
                            "ok": "Processing Images"
                        }
                        self.assertEqual(resp.status_code, 200)
                        self.assertEqual(loads(resp.data), expected)

    def test_status_ok_with_batch_size(self):
        data = {'filepath': '/redpoints/src/dependencies/images.tsv', 'batch_size': 5}

        images_tsv = "id\turl\n0\thttps://www.url.com/blank_image"
        blank = Image.new('RGB', (64,64))
        img_buf = None
        with BytesIO() as output:
            blank.save(output, format="GIF")
            img_buf = output.getvalue()
            blank_img = Image.open(BytesIO(img_buf))

        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=images_tsv)):
                with requests_mock.mock() as m:
                    with self.app.test_client() as cli:
                        m.get('https://www.url.com/blank_image', content=img_buf)
                        resp = cli.post('/api/v1/batch_predict/', json=data)
                        expected = {
                            "ok": "Processing Images"
                        }
                        self.assertEqual(resp.status_code, 200)
                        self.assertEqual(loads(resp.data), expected)

    def test_status_422_data_is_not_provieded(self):
        with self.app.test_client() as cli:
            resp = cli.post('/api/v1/batch_predict/')
            expected = {
                "error": "Data is not provided"
            }
            self.assertEqual(resp.status_code, 422)
            self.assertEqual(loads(resp.data), expected)

    def test_status_422_filepath_does_not_exists(self):
        data = {'filepath': '/redpoints/src/dependencies/images.tsv'}

        with patch('os.path.exists', return_value=False):
            with self.app.test_client() as cli:
                resp = cli.post('/api/v1/batch_predict/', json=data)
                expected = {
                    "error": "Invalid input file url"
                }
                self.assertEqual(resp.status_code, 422)
                self.assertEqual(loads(resp.data), expected)
