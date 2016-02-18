import json
import os

from collections import OrderedDict

_file_cache = {}


def get_json_file(path):
    if _file_cache.get(path):
        return _file_cache[path]

    with open(path) as f:
        out = json.load(f, object_pairs_hook=OrderedDict)

    _file_cache[path] = out

    return out


def get_indicators():
    indicators_file = os.path.join(os.path.dirname(__file__),
                                   'static', 'data', 'indicators.json')
    return get_json_file(indicators_file)


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


def get_map_indicators():
    map_indicators = _file_cache.get('map_indicators', [])
    if not map_indicators:
        indicators = get_indicators()
        level_1_indicators = {}
        level_2_indicators = []
        for code, indicator in indicators.iteritems():
            if (indicator['level'] <= 2 and not code[-1].isalpha()):
                map_indicator = indicator.copy()
                map_indicator['code'] = code
                if map_indicator['level'] == 1:
                    if not map_indicator.get('subindicators'):
                        map_indicator['subindicators'] = []
                    level_1_indicators[code] = map_indicator
                    map_indicators.append(map_indicator)
                else:
                    level_2_indicators.append(map_indicator)
        for level_2_indicator in level_2_indicators:
            code = level_2_indicator['code'][:1]
            level_1_indicators[code]['subindicators'].append(level_2_indicator)
        _file_cache['map_indicators'] = map_indicators
    return map_indicators
