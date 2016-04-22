import json
import math

import jmespath
import re

import requests
import tempfile

from PIL import Image
from django.conf import settings
import os


def api_url(func):
    return "https://api-u.spaziodati.eu/{}?token={}".format(func, settings.SD_TOKEN)


def check_resp(resp):
    if resp.status_code != 200:
        raise Exception("URL [{}] got status {} with content: {}".format(
            resp.url,
            resp.status_code,
            resp.content
        ))


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
                check_resp(resp)

                result = resp.json()
                if result['IsErroredOnProcessing']:
                    raise Exception('OCR API fucked you: {}'.format(json.dumps(result)))
                if result['ParsedResults'] is None:
                    return ''
                return result['ParsedResults'][0]['ParsedText']
        finally:
            os.remove(fname)

    def get_company_list(self):
        ocr_text = self.get_ocr_data()

        good_vat = self.search_for_piva(ocr_text)
        if good_vat:
            return self.anagrafica_by_vat(good_vat)
        else:
            return []

    def anagrafica_by_vat(self, vat):
        resp = requests.get(api_url('azienda/anagrafica')+'&piva={}'.format(vat))
        check_resp(resp)
        result = resp.json()
        if result['meta']['items'] == 0:
            return []
        else:
            item = result['results'][0]
            return [{
                'label': item['denominazione'],
                'province': item['sede']['provincia'],
                'atoka_link': item['link_atoka'],
                'sector': item['descrizione'],
                'vat': item['piva']
            }]

    def search_for_piva(self, text):
        resp = requests.post(
            api_url('datatxt/nex/v1'),
            data={
                'include': 'types',
                'extra_types': 'vat',
                'text': text,
                'country': 'it',
                'min_confidence': 0
            }
        )
        check_resp(resp)
        result = resp.json()
        vatcodes = jmespath.search(
            "annotations[?types == ['http://dandelion.eu/ontology#vatID']].title",
            result
        )
        if vatcodes:
            return vatcodes[0][2:]
        else:
            return None



