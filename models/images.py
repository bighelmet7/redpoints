import numpy as np
from collections import deque
from io import BytesIO

from PIL import Image, ImageFile
from requests.exceptions import ReadTimeout
from simplejson import dumps

from exceptions import ImageInfoError
from mlteam.extensions import session as ext_session

# ISSUE: https://github.com/python-pillow/Pillow/issues/1510
ImageFile.LOAD_TRUNCATED_IMAGES = True


class ImageInfo(object):
    """
    Stores the information of an image.
    """

    def __init__(self, id, url, session=None):
        self.id = id
        self.url = url
        self.image_size = None
        self._session = session if session else ext_session

    def _get_image(self):
        """
        Return a PIL.Image class constructed from the given image URL if it is
        valid.
        Note: An image is considered valid if it was able to be downloaded from
        the given URL and it was able to be opened with PIL.
        """
        try:
            response = self._session.get(self.url, timeout=10)
        except ReadTimeout:
            raise ImageInfoError('Timeout while requesting Image.')
        if response:
            try:
                self.image_size = len(response.content)
                return Image.open(BytesIO(response.content))
            except IOError:
                raise ImageInfoError('Image could not be opened.')
        raise ImageInfoError('Image could not be requested.')

    def resize(self, x=64, y=64):
        """
        Resize the image x * y. Returns a NumPy array of size
        (n_channels, x, y) of the image resized and the n_channels of the image.
        """
        try:
            img = self._get_image()
        except ImageInfoError as e:
            return np.zeros(1).tolist(), 0
        r_img = img.resize((x, y,))
        result = np.array(r_img)
        n_channels = len(r_img.getbands())
        img.close()
        r_img.close()
        return result.tolist(), n_channels

    def to_dict(self):
        """
        Returns a dictionary with the current image info.
        """
        try:
            img = self._get_image()
            result = {
                "url": self.url,
                "image_info": {
                    "image_size": self.image_size,
                    "image_dimension": img.size,
                    "image_format": img.format,
                }
            }
        except ImageInfoError as e:
            result = {
                "url": self.url,
                "image_info": "",
                "error": str(e),
            }
        else:
            img.close()
        return result


class BatchImage(object):
    """
    Represents a batch of images.
    """
    def __init__(self, images=[], batch_size=0, session=None):
        self.batch_images = images
        self.batch_size = batch_size
        self._session = session if session else ext_session

    def resize_batch_images(self, x=64, y=64, redis_conn=None):
        """
        Resize all images to x * y in batches of 'batch_size'. If redis_conn
        is not None, the values are pushed to a queue:batch.
        """
        counter = 0
        images = deque()
        for image in self.batch_images:
            if counter < self.batch_size:
                img = ImageInfo(image.id, image.url, session=self._session)
                # if its a batch every image has its own channel but the result 
                # should be: {batch_size: '(batch_size, ch, 64, 64)', ...}
                r_img, n_channels = img.resize(x, y)
                images.append(r_img)
                counter += 1
            if counter == self.batch_size:
                if redis_conn is not None:
                    batch_dimension = '({batch_size}, {ch}, {x}, {y})'.format(
                        batch_size=self.batch_size,
                        ch=n_channels,
                        x=x,
                        y=y
                    )
                    result = {
                        'batch_dimension': batch_dimension,
                        'images': list(images)
                    }
                    redis_conn.rpush('queue:batch', dumps(result))
                counter = 0
                images.clear()
