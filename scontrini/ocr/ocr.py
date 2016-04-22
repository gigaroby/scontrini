import requests
import tempfile

from PIL import Image
from django.conf import settings
import os


class OcrReceipt(object):

    OCR_API_ENDPOINT = 'https://api.ocr.space/parse/image'

    def __init__(self, filename):
        self.filename = filename
        self.scaled_filename = None

    def scale_image(self):
        original_size = os.path.getsize(self.filename)
        if original_size > settings.OCR_SIZE_LIMIT:
            with Image.open(self.filename) as original:
                w, h = original.size
                ratio = original_size / settings.OCR_SIZE_LIMIT
                scaled_w = w / ratio
                scaled_h = h / ratio
                original.thumbnail((scaled_w, scaled_h))
                temp = tempfile.mkstemp()
                original.save(temp.name)
                return temp
        else:
            return open(self.filename)

    def get_ocr_data(self):
        payload = {
            'apikey': settings.OCR_API_KEY,
            'language': 'ita'
        }
        with self.scale_image() as scan:
            resp = requests.post(
                self.OCR_API_ENDPOINT,
                data={'apikey': settings.OCR_API_KEY, 'language': 'it'},
                file=scan
            )
            if resp.status_code != 200:
                raise Exception('OCR API returned {}: {}'.format(resp.status_code, resp.content))

            result = resp.json()
            return result
