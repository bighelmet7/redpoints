from io import BytesIO
from PIL import Image
from exceptions import ImageInfoError
from requests.exceptions import ReadTimeout
from requests import Session


class ImageInfo(object):
    """
    Stores the information of an image.
    """

    def __init__(self, id, url, session=None):
        self.id = id
        self.url = url
        self.image_size = None
        self._session = session if session else Session()

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
