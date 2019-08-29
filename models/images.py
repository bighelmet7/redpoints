from io import BytesIO
from PIL import Image
from exceptions import ImageInfoError
from requests import get as GET


class ImageInfo(object):
    """
    Stores the information of an image.
    """

    def __init__(self, id, url):
        self.id = id
        self.url = url
        self._img = self._get_image()

    def _get_image(self):
        """
        Return a PIL.Image class constructed from the given image URL if it is
        valid.
        Note: An image is considered valid if it was able to be downloaded from
        the given URL and it was able to be opened with PIL.
        """
        response = GET(self.url, timeout=10)
        if response:
            try:
                return Image.open(BytesIO(response.content))
            except IOError:
                raise ImageInfoError('Image could not be opened.')
        raise ImageInfoError('Image could not be requested.')

    def to_dict(self):
        """
        Returns a dictionary with the current image info.

        Note: if this method is called the _img attribute will not hold the
        Image class anymore for avoiding memory leaks.
        """
        result = {
            "image_size": len(self._img.tobytes()),
            "image_dimension": self._img.size,
            "image_format": self._img.format,
        }
        self._img.close()
        return result
