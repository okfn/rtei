import json
import os

from collections import OrderedDict
from django.conf import settings

_file_cache = {}


def get_json_file(path, ordered_dict=True):
    if _file_cache.get(path):
        return _file_cache[path]

    with open(path) as f:
        if ordered_dict:
            out = json.load(f, object_pairs_hook=OrderedDict)
        else:
            out = json.load(f)

    _file_cache[path] = out

    return out


def get_file_path(file_name, year=''):
    return os.path.join(
        os.path.dirname(__file__),
        'static', 'data',
        year,
        file_name)


def get_indicators(year):
    indicators_file = get_file_path('indicators.json', year)
    return get_json_file(indicators_file, ordered_dict=False)


def get_themes(year):
    themes_file = get_file_path('themes.json', year)
    return get_json_file(themes_file, ordered_dict=False)


def get_countries():
    countries_file = os.path.join(os.path.dirname(__file__),
                                  '..', 'data', 'countries.json')
    return get_json_file(countries_file)


def get_scores_per_country(year):
    scores_file = get_file_path('scores_per_country.json', year)
    return get_json_file(scores_file)


def get_c3_scores_per_country(year):
    scores_file = get_file_path('c3_scores_per_country.json', year)
    return get_json_file(scores_file)


def get_indicators_for_country(country_code, year):
    country_file = get_file_path('{0}.json'.format(country_code), year)
    if not os.path.exists(country_file):
        return None

    return get_json_file(country_file)


def get_countries_with_data():
    year = settings.YEARS[-1]
    scores_file = get_file_path('countries_with_data.json', year)
    return get_json_file(scores_file)


def get_country_name(country_code):
    '''
    Given a country code, return the corresponding country name.
    '''
    code_type = 'iso2'
    if len(country_code) == 3:
        code_type = 'iso3'

    return next(
        (c['name'] for code, c in get_countries().items()
         if c[code_type] == country_code.upper()),
        None)
