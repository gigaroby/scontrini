import json
import math
import re

import requests
import tempfile

from PIL import Image
from django.conf import settings
import os


class OcrReceipt(object):

    OCR_API_ENDPOINT = 'https://api.ocr.space/parse/image'

    def __init__(self, filename):
        self.filename = filename

    def scale_image(self):
        original_size = os.path.getsize(self.filename)
        current_size = original_size
        scale_factor = 1.75
        if current_size > settings.OCR_SIZE_LIMIT:
            with Image.open(self.filename) as original:
                w, h = original.size
                ratio = original_size / settings.OCR_SIZE_LIMIT / scale_factor
                scaled_w = w / ratio
                scaled_h = h / ratio
                original.thumbnail((scaled_w, scaled_h), resample=0)
                f, name = tempfile.mkstemp(suffix='.png')
                os.close(f)
                original.save(name)
                return name
        else:
            return self.filename

    def get_ocr_data(self):
        fname = self.scale_image()
        try:
            with open(fname, 'rb') as f:
                resp = requests.post(
                    self.OCR_API_ENDPOINT,
                    data={'apikey': settings.OCR_API_KEY, 'language': 'ita'},
                    files={'receipt': f}
                )
                if resp.status_code != 200:
                    raise Exception('OCR API returned {}: {}'.format(resp.status_code, resp.content))

                result = resp.json()
                if result['IsErroredOnProcessing']:
                    raise Exception('OCR API fucked you: {}'.format(json.dumps(result)))
                if result['ParsedResults'] is None:
                    return ''
                return result['ParsedResults'][0]['ParsedText']
        finally:
            os.remove(fname)
