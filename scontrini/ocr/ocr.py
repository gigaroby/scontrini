import json
from _operator import itemgetter
import re

import jmespath
import os
import requests
import tempfile
from PIL import Image
from django.conf import settings


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
        self.ocr_text = None
        self.companies = []
        self.totals = []

    def parse(self):
        self.ocr_text = self.get_ocr_data()
        if self.ocr_text is None:
            self.ocr_text = ''
        self.companies = self.get_company_list()
        self.remove_duplicates()
        self.enrich_company_list()
        self.totals = self.get_totals()

    def get_totals(self):
        all_numbers = re.findall(r'\b\s?\d+[\.,]\s?\d{2}\b', self.ocr_text)
        all_numbers = [x.replace(' ', '').replace(',', '.') for x in all_numbers]
        all_numbers_int = set()
        for i in all_numbers:
            try:
                all_numbers_int.add(float(i))
            except:
                pass
        all_numbers_int = sorted(list(all_numbers_int), reverse=True)
        return all_numbers_int[:3]

    def scale_image(self):
        original_size = os.path.getsize(self.filename)
        current_size = original_size
        scale_factor = 1.75
        if current_size > settings.OCR_SIZE_LIMIT:
            with Image.open(self.filename) as original:
                while True:
                    w, h = original.size
                    ratio = original_size / settings.OCR_SIZE_LIMIT / scale_factor
                    scaled_w = w / ratio
                    scaled_h = h / ratio
                    original.thumbnail((scaled_w, scaled_h), resample=0)
                    f, name = tempfile.mkstemp(suffix='.png')
                    os.close(f)
                    original.save(name)
                    current_size = os.path.getsize(name)
                    if current_size < settings.OCR_SIZE_LIMIT:
                        return name
                    else:
                        scale_factor += 0.05
                        os.remove(name)
        else:
            return self.filename

    def get_ocr_data(self):
        fname = self.scale_image()
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

    def get_company_list(self):
        if not self.ocr_text.strip():
            return []

        with_good_vat = self.search_for_piva_with_datatxt(self.ocr_text)
        if with_good_vat:
            return with_good_vat

        with_potential_vat = self.search_for_pivas_with_regex(self.ocr_text)
        if with_potential_vat:
            return with_potential_vat

        with_company_names = self.search_with_companytxt(self.ocr_text)
        if with_company_names:
            return with_company_names
        else:
            return []

    def remove_duplicates(self):
        new_list = []

        def search_by_piva(l, achene):
            for i in l:
                if i['id'] == achene:
                    return True
            return False

        for company in self.companies:
            if not search_by_piva(new_list, company['id']):
                new_list.append(company)

        self.companies = new_list

    def enrich_company_list(self):
        for company in self.companies:
            resp = requests.get(
                api_url('v2/companies/{}'.format(company['id'])),
                params={'packages': '*'}
            )
            check_resp(resp)
            detail = resp.json()
            coords = jmespath.search('item.locations.items[?address.lon].address.[lon, lat]', detail)
            company['locations'] = coords

            company['people'] = jmespath.search(
                'item.people.items[].{"name": name, "birthday": birthDate, "role": roles[0].name}',
                detail
            )

    def anagrafica_by_vat(self, vat, fuzzy=0):
        resp = requests.get(api_url('azienda/anagrafica'), params={'piva': vat, 'fuzzy': 0})
        check_resp(resp)
        result = resp.json()
        if result['meta']['items'] == 0:
            return []
        else:
            return [{
                'label': item['denominazione'],
                'province': item['sede']['provincia'],
                'atoka_link': item['link_atoka'],
                'sector': item['descrizione'],
                'vat': item['piva'],
                'id': item['acheneID'][35:47],
                'ateco_code': item['codice_ateco'][-1]
            } for item in result['results']]

    def search_for_piva_with_datatxt(self, text):
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
            return self.anagrafica_by_vat(vatcodes[0][2:])
        else:
            return []

    def search_for_pivas_with_regex(self, text):
        all_results = []

        potential_pivas = re.findall('\b\d{10,11}\b', text)
        potential_piva_text = 'P.IVA ' + ' P.IVA'.join(potential_pivas)

        valid_pivas = self.search_for_piva_with_datatxt(potential_piva_text)
        if valid_pivas:
            for piva in valid_pivas:
                all_results += self.anagrafica_by_vat(piva)
            if all_results:
                return all_results

        # nessuna piva valida
        for piva in potential_pivas:
            all_results += self.anagrafica_by_vat(piva, fuzzy=1)
            if all_results:
                return all_results

        # search with fuzzy 2
        for piva in potential_pivas:
            all_results += self.anagrafica_by_vat(piva, fuzzy=2)

        return all_results

    def search_with_companytxt(self, text):
        resp = requests.post(
            api_url('v2/companies/annotate'),
            data={
                'text': text,
                'min_confidence': 0.1,
                'include': 'sameAs'
            }
        )
        check_resp(resp)
        result = resp.json()
        all_companies = jmespath.search('annotations[?sameAs.vatUrn]', result)
        if not all_companies:
            return []
        else:
            all_companies = sorted(all_companies, key=itemgetter('confidence'), reverse=True)
            pivas = [i['sameAs']['vatUrn'][7:] for i in all_companies]
            all_results = []
            for piva in pivas:
                all_results += self.anagrafica_by_vat(piva)
            return all_results



