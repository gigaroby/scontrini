# this mapping is generated, do not edit
# the original data is contained in ateco-friendly.txt
# the script to generate this mapping is r.py
MAPPING = {'01.1': 'Spesa',
           '01.2': 'Spesa',
           '01.3': 'Spesa',
           '01.4': 'Spesa',
           '01.5': 'Altro',
           '01.6': 'Altro',
           '01.7': 'Spesa',
           '02': 'Altro',
           '03.1': 'Spesa',
           '03.2': 'Altro',
           '05': 'Altro',
           '06': 'Altro',
           '07': 'Altro',
           '08': 'Altro',
           '09': 'Altro',
           '10': 'Spesa',
           '11': 'Spesa',
           '12': 'Altro',
           '13': 'Vestiti',
           '14': 'Vestiti',
           '15': 'Vestiti',
           '16': 'Altro',
           '17': 'Altro',
           '18.1': 'Altro',
           '18.2': 'Altro',
           '19': 'Altro',
           '20': 'Altro',
           '21': 'Spesa',
           '22': 'Altro',
           '23': 'Altro',
           '24': 'Altro',
           '25': 'Altro',
           '26.1': 'Intrattenimento',
           '26.2': 'Intrattenimento',
           '26.3': 'Intrattenimento',
           '26.4': 'Intrattenimento',
           '26.5': 'Intrattenimento',
           '26.6': 'Intrattenimento',
           '26.7': 'Intrattenimento',
           '26.8': 'Intrattenimento',
           '27': 'Altro',
           '28': 'Altro',
           '29': 'Automobile',
           '30': 'Altro',
           '31': 'Altro',
           '32': 'Altro',
           '33': 'Altro',
           '35': 'Bollette',
           '36': 'Bollette',
           '37': 'Bollette',
           '38': 'Bollette',
           '39': 'Bollette',
           '41': 'Altro',
           '42': 'Altro',
           '43': 'Altro',
           '45': 'Altro',
           '46': 'Altro',
           '47.1': 'Spesa',
           '47.2': 'Spesa',
           '47.3': 'Automobile',
           '47.4': 'Intrattenimento',
           '47.51': 'Spesa',
           '47.52': 'Altro',
           '47.53': 'Altro',
           '47.54': 'Altro',
           '47.59': 'Altro',
           '47.61': 'Intrattenimento',
           '47.62': 'Intrattenimento',
           '47.63': 'Intrattenimento',
           '47.64': 'Intrattenimento',
           '47.65': 'Intrattenimento',
           '47.71': 'Spesa',
           '47.72': 'Altro',
           '47.73': 'Spesa',
           '47.74': 'Spesa',
           '47.75': 'Altro',
           '47.76': 'Altro',
           '47.77': 'Altro',
           '47.78': 'Altro',
           '47.79': 'Altro',
           '47.8': 'Altro',
           '47.9': 'Altro',
           '49': 'Altro',
           '50': 'Altro',
           '51': 'Altro',
           '52': 'Altro',
           '53': 'Altro',
           '55': 'Alberghi e ristoranti',
           '56': 'Alberghi e ristoranti',
           '58': 'Intrattenimento',
           '59': 'Intrattenimento',
           '60': 'Intrattenimento',
           '61': 'Intrattenimento',
           '62': 'Intrattenimento',
           '63': 'Intrattenimento',
           '64': 'Bollette',
           '65': 'Bollette',
           '66': 'Bollette',
           '68.1': 'Altro',
           '68.2': 'Affitto',
           '68.3': 'Altro',
           '69': 'Altro',
           '70': 'Altro',
           '71': 'Altro',
           '72': 'Altro',
           '73': 'Altro',
           '74': 'Altro',
           '75': 'Altro',
           '77': 'Altro',
           '78': 'Altro',
           '79': 'Alberghi e ristoranti',
           '80': 'Altro',
           '81': 'Altro',
           '82': 'Altro',
           '84': 'Altro',
           '85': 'Bollette',
           '86': 'Bollette',
           '87': 'Bollette',
           '88': 'Bollette',
           '90': 'Intrattenimento',
           '91': 'Intrattenimento',
           '92': 'Intrattenimento',
           '93': 'Intrattenimento',
           '94': 'Altro',
           '95': 'Altro',
           '96': 'Altro',
           '97': 'Altro',
           '98': 'Altro',
           '99': 'Altro'}


def _parse_ateco(ateco):
    first = [ateco[:2]]
    rest = [c for c in ateco[2:] if c != '.']
    return first + rest


def _join_ateco(fragments):
    first, *frags = fragments
    result = []

    if frags and len(frags) % 2 == 1:
        result.append(frags.pop())

    while frags:
        second = frags.pop()
        first = frags.pop()
        result.append(first + second)

    result.append(first)
    result.reverse()
    return '.'.join(result)


def ateco_to_category(ateco):
    fragments = _parse_ateco(ateco)
    while fragments:
        attempt = _join_ateco(fragments)
        if attempt in MAPPING:
            return MAPPING[attempt]

        fragments.pop()

    return 'Altro'


def get_categories():
    return {x for _, x in MAPPING.items()}

