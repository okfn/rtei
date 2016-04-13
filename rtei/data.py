import json
import os

from collections import OrderedDict

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


def get_indicators():
    indicators_file = os.path.join(os.path.dirname(__file__),
                                   'static', 'data', 'indicators.json')
    return get_json_file(indicators_file, ordered_dict=False)


def get_themes():
    themes_file = os.path.join(os.path.dirname(__file__),
                               'static', 'data', 'themes.json')
    return get_json_file(themes_file, ordered_dict=False)


def get_themes_mappings():
    themes_file = os.path.join(os.path.dirname(__file__),
                               'static', 'data', 'themes_mappings.json')
    return get_json_file(themes_file, ordered_dict=False)


def get_countries():
    countries_file = os.path.join(os.path.dirname(__file__),
                                  '..', 'data', 'countries.json')
    return get_json_file(countries_file)


def get_scores_per_country():
    scores_file = os.path.join(os.path.dirname(__file__),
                               'static', 'data', 'scores_per_country.json')
    return get_json_file(scores_file)


def get_c3_scores_per_country():
    scores_file = os.path.join(os.path.dirname(__file__),
                               'static', 'data', 'c3_scores_per_country.json')
    return get_json_file(scores_file)


def get_indicators_for_country(country_code):
    country_file = os.path.join(os.path.dirname(__file__),
                                'static', 'data',
                                '{0}.json'.format(country_code))
    if not os.path.exists(country_file):
        return None

    return get_json_file(country_file)


def get_country_name(country_code):
    '''
    Given a country code, return the corresponding country name.
    '''
    code_type = 'iso2'
    if len(country_code) == 3:
        code_type = 'iso3'

    return next(
        (c['name'] for code, c in get_countries().iteritems()
         if c[code_type] == country_code.upper()),
        None)
