#!/usr/bin/env python
'''
Data script for the RTEI website.

Check ./build_data.py -h for details
'''
import re
import os
import json
import csv
import argparse
import random
from collections import OrderedDict

from openpyxl import load_workbook

INPUT_FILE = 'data/rtei_data_2015.xlsx'
COUNTRIES_FILE = 'data/countries.json'
OUTPUT_DIR = 'rtei/static/data'

CORE_SHEET = 'Core Questionnaire'
COMPANION_SHEET = 'Companion Questionnaire'
THEMES_SHEET = 'Transversal Themes'
THEMES_MAPPINGS_SHEET = 'Transversal Themes Mappings'

MODIFIERS = {
    'gp': 'Gender Parity',
    'ad': 'Advantaged Group',
    'resp': 'Residential Parity',
    'disp': 'Disability Parity',
    # These are underscores in the spreadsheet
    'inc-hmp': 'High to Medium Quartile Income Ratio',
    'inc-mlp': 'Medium to Low Quartile Income Ratio',
}

SCHOOL_TYPES = {
    'a': 'Primary schools',
    'b': 'Secondary schools',
    'c': 'TVET',
    'd': 'Tertiary schools',
    'e': 'Private Primary schools',
    'f': 'Private Secondary schools',
    'g': 'Private TVET',
    'h': 'Private Tertiary schools',
}

# Excel handler
wb = None

# Countries dictionary
countries = None

'''
This will match any codes at the beginning of the string, starting with
a number and ending with a colon, eg:
1:
1.1:
1.1.1aa:
1.1.1a_emp_dis:
'''
valid_code = re.compile(r'^(C )?(\d)(.*?)?:')


def get_country_code(country_name, code_type='iso2'):
    '''
    Given a country name, return its ISO code

    By default to the 2 digit code is returned (eg 'AF' for Afghanistan),
    passing code_type='iso3' will return the 3 digit code (eg'AFG').
    '''
    if not country_name:
        return None
    for code, country in countries.iteritems():
        if (country_name == country['name'] or
            ('other_names' in country and
             country_name == country.get('other_names'))):
            return country[code_type]
    return None


def get_country_name(country_code):
    '''
    Given a country code, return the corresponding country name.
    '''
    code_type = 'iso2'
    if len(country_code) == 3:
        code_type = 'iso3'

    return next(
        (c['name'] for code, c in countries.iteritems()
         if c[code_type] == country_code.upper()),
        None)


def get_numeric_cell_value(cell):
    '''
    Return a numeric value rounded to 2 places if it is a float, or the value
    otherwise
    '''
    if isinstance(cell.value, float):
        return round(cell.value, 2)
    else:
        return cell.value


def get_level_for_indicator(code):

    if code.count('.') == 0:
        # 1
        level = 1
    elif code.count('.') == 1:
        # 1.2
        level = 2
    elif code.count('.') == 2:
        try:
            int(code.replace('.', ''))
            # 1.3.4
            level = 3
        except ValueError:
            # 1.5.6a or 1.5.6a_dis
            level = 4
    else:
        raise ValueError('Wrong indicator code: {0}'.format(code))

    return level


def get_level_for_theme(code):
    if not code[-1].isalpha():
        # 1
        level = 1
    else:
        # 1A or 1A.B
        level = 2
    return level


def parse_cell(value, theme=False):
    '''
    Parses an indicator cell to return a tuple with its code, title and level

    Indicator cells must have one of the following formats:

    * {code}: {title}
    * {code}

    Codes must start with a number but they can be pretty much anything else
    after it.
    If there is no title available, for a limited set of conditions it will be
    generated (codes ending in `_year` and those ending in one of the
    MODIFIERS)

    The level is calculated from the code, checking for the number of `.`
    characters and extra modifiers.

    Returns a tuple (code, title, level), with any of the values set to None if
    it could not be computed (which should not happen).
    '''

    code = None
    title = None
    level = None

    match = valid_code.match(value)
    if match:
        groups = match.groups()
        code = ''.join(g for g in groups if g and g != 'C ')
        title = value \
            .replace(code + ':', '') \
            .replace('C ', '') \
            .strip()
        level = (get_level_for_theme(code) if theme
                 else get_level_for_indicator(code))
    elif '_year' in value.split()[0]:
        code = value.split()[0]
        title = 'Year'
        level = 4
    elif any(modifier in value.split()[0] for modifier in MODIFIERS.keys()):
        # This is a derived indicator, we compute the title automatically
        # in the form:
        #   School type: Modifer - Modifier

        parts = value.replace('inc_', 'inc-').split('_')
        title_parts = []
        for part in parts[1:]:
            title_parts.append(MODIFIERS[part])
        school_type = SCHOOL_TYPES.get(parts[0][-1], '')
        title = '{0}: {1}'.format(school_type, ' - '.join(title_parts))
        code = value.split()[0]
        level = 4

    return code, title, level


def get_themes_mappings():
    ''' Returns a dict with the Transversal Themes mappings

    Keys are the TT code (eg "1A.A") and values are a list of dicts with
    indicator ids and titles, eg:

    {
        "1A.A": [
            {
                "code": "1.4.4j",
                "title": "Is data disaggregated by disability status?"
            },
            {
                "code": "3.2.1j",
                "title": "Do national laws forbid discrimination in education by disability status?"
            },
        ],

     }
    '''

    out = {}
    sheet = THEMES_MAPPINGS_SHEET
    ws = wb[sheet]

    for i in xrange(2, len(ws.columns[1:])):
        theme_cell = ws.columns[i][1]  # Row 2
        if theme_cell.value:
            theme_code, theme_title, theme_level = parse_cell(theme_cell.value,
                                                              theme=True)
            if theme_code:
                out[theme_code] = []
                indicators_column = ws.columns[i + 1]
                for cell in indicators_column:
                    if cell.value:
                        code, title, level = parse_cell(cell.value)
                        if code:
                            out[theme_code].append({'code': code,
                                                    'title': title})

    return out


def get_themes(include_columns=False, only_with_values=True,
               include_indicators=False):
    '''
    Returns a list of dicts describing the transversal themes. Each of the
    dicts contains the following keys:

        * `code`: The unique identifier for this indicator, examples include
            1, 1.A, 1.A.B
        * `title`: The string that describes the indicator.
        * `level`: The hierarchy of the indicator (level 1 or 2)
        * `column` (optional, only if `include_columns` is True): The column on
            the spreadsheet that holds the values for the indicator.

    '''

    out = []
    sheet = THEMES_SHEET
    ws = wb[sheet]
    if include_indicators:
        mappings = get_themes_mappings()

    codes_done = []
    for i in (1, 2):
        for cell in ws.rows[i]:
            theme = None
            if cell.value:
                code, title, level = parse_cell(cell.value, theme=True)
                if not code or code in codes_done:
                    continue
                codes_done.append(code)

                if only_with_values:
                    # Check if the theme actually has values on the spreadsheet
                    value_cell = ws[cell.column + '4']
                    if not type(value_cell.value) in (float, long, int):
                        continue

                theme = {
                    'code': code,
                    'title': title,
                    'level': level
                }
                if include_indicators and code in mappings:
                    theme['indicators'] = mappings[code]

                out.append(theme)
                if i == 2 and include_columns:
                    theme['column'] = cell.column
    return out


def get_indicators(core=True, include_columns=False):
    '''
    Returns a list of dicts describing the indicators. Each of the dicts
    contains the following keys:

        * `code`: The unique identifier for this indicator, examples include
            1, 2.3, 3.3.4, 1.3a, 2.2.1_year, 3.2.1a_resp_ad.
        * `title`: The string that describes the indicator.
        * `level`: The hierarchy of the indicator. Without taking the derived
            indicators into account this is straight forward: 1 -> 1, 1.1 -> 2,
            1.1.1 -> 3, 1.1.1a -> 4. Derived indicators can have the following
            levels: 1.2a -> 2 and 1.1.1a_resp_ad -> 4.
        * `core`: Whether the indicator is part of the Core or the Companion
            questionnaire. The ones to return are controlled with the `core`
            parameter.
        * `column` (optional, only if `include_columns` is True): The column on
            the spreadsheet that holds the values for the indicator.

    '''

    out = []
    if core:
        sheet = CORE_SHEET
    else:
        sheet = COMPANION_SHEET
    ws = wb[sheet]

    # First four rows
    # We skip row 2 as values are duplicated on row 4
    codes_done = []
    for i in (0, 2, 3):
        for cell in ws.rows[i]:
            indicator = None
            if cell.value:
                code, title, level = parse_cell(cell.value)
                if not code:
                    continue
                if code in codes_done:
                    if i == 3:
                        # Use the previous one
                        indicator = [o for o in out if o['code'] == code][0]
                    else:
                        continue
                elif '_year' in code and i == 3:
                    indicator = [o for o in out
                                 if o['code'] == code.replace('_year', '')][0]
                else:
                    codes_done.append(code)

                if not indicator:
                    indicator = {
                        'code': code,
                        'title': title,
                        'core': core,
                        'level': level
                    }
                    out.append(indicator)
                if i == 3 and include_columns:
                    if title == 'Response':
                        indicator['column_response'] = cell.column
                    elif '_year' in code:
                        indicator['column_year'] = cell.column
                    else:
                        indicator['column'] = cell.column
            else:
                # Other indicators
                # print cell.value
                pass
    return out


def get_all_indicators(include_columns=False):
    '''
    Returns a list of all indicators. See get_indicators for details.
    '''

    core_indicators = get_indicators(include_columns=include_columns)

    core_codes = [q['code'] for q in core_indicators]

    companion_indicators = get_indicators(core=False,
                                          include_columns=include_columns)

    # Remove duplicates
    for indicator in companion_indicators:
        if indicator['code'] not in core_codes:
            core_indicators.append(indicator)

    indicators = sorted(core_indicators, key=lambda k: k['code'])

    return indicators


def get_main_scores(country_indicators):
    '''
    Return the values for the level 1 indicators (ie 1, 2, 3, 4 and 5)

    These are computed with the average of all level 2 indicators (eg 1.1,
    1.2, etc). These are returned as a percentage rounded to 2 decimal
    places.
    '''

    scores = {}
    for code, value in country_indicators.iteritems():
        if code == 'index':
            continue

        if code[:1] not in scores:
            scores[code[:1]] = []

        if code.count('.') == 1 and not code[-1].isalpha() and value is not None:
            scores[code[:1]].append(value * 100 if value <= 1 else value)

    return {score: round(sum(values) / len(values), 2) for score, values in scores.iteritems() if values}


def add_main_scores(country_indicators):
    '''
    Add the values for the level 1 indicators (ie 1, 2, 3, 4 and 5) to the
    passed country_indicators dict.
    '''
    country_indicators.update(get_main_scores(country_indicators))


def get_full_score(country_indicators):
    '''
    Return an object {'index':<num>}, where number is the computed average of
    all level 1 indicators (ie 1, 2, 3, 4 and 5) returned as a percentage
    rounded to 4 decimal places.
    '''
    values = [country_indicators[str(code)] for code in xrange(1, 6)
              if str(code) in country_indicators]
    return {'index': round(sum(values) / len(values), 2)}


def add_full_score(country_indicators):
    '''
    Add the full overall score to the country indicators with the `index` key.
    '''
    country_indicators.update(get_full_score(country_indicators))


def indicators_per_country(max_level=4, derived=True, random_values=False,
                           responses=True):
    '''
    Returns a dict containing the values for all indicators for all countries,
    with the following structure:

        {
            'CL': {
                    '1': 64.76,
                    '1.1': 100.0,
                    '1.1.1a': 'Yes',
                    '1.1.1b': 'Yes',
                    '1.1.1c': 'Yes',
                    # ...
                    },
            'TZ': {
                    '1': 74.736,
                    '1.1': 100.0,
                    '1.1.1a': 'Yes',
                    '1.1.1b': 'No',
                    '1.1.1c': 'Yes',
                    # ...
                    },

            # ...
        }

    If responses is False, the actual indicator value is returned:
        {
            'CL': {
                    '1': 64.76,
                    '1.1': 100.0,
                    '1.1.1a': 1,
                    '1.1.1b': 1,
                    '1.1.1c': 1,
                    # ...
                    },
            'TZ': {
                    '1': 74.736,
                    '1.1': 100.0,
                    '1.1.1a': 1,
                    '1.1.1b': 0,
                    '1.1.1c': 1,
                    # ...
                    },

            # ...
        }

    You can restrict the indicators returned with the `max_level` parameter
    and whether to return `derived` (eg 1.2a or 3.2.1_ag) indicators or not.

    If `random_values` is True, countries not present in the spreadsheet are
    returned with random values (only for levels 1 and 2).
    '''

    out = OrderedDict()

    indicators = get_all_indicators(include_columns=True)

    ws_core = wb[CORE_SHEET]
    ws_companion = wb[COMPANION_SHEET]
    country_codes = []
    for i in xrange(5, len(ws_core.rows) + 1):
        country_name = ws_core['A' + str(i)].value
        if not country_name:
            continue
        country_code = get_country_code(country_name)
        if not country_code:
            print 'Warning: Could not get country code for {0}'.format(
                country_name)
        country_codes.append(country_code)
        out[country_code] = OrderedDict()
    for i, country_code in enumerate(country_codes):
        for indicator in indicators:
            if indicator['level'] <= max_level and indicator.get('column'):
                if not derived and indicator['code'][-1].isalpha():
                    # Avoid derived indicators (eg 1.2a or 3.2.1_ag)
                    continue
                if responses and indicator.get('column_response'):
                    cell = indicator['column_response'] + str(i + 5)
                else:
                    cell = indicator['column'] + str(i + 5)
                if indicator['core']:
                    worksheet = ws_core
                else:
                    worksheet = ws_companion

                value = get_numeric_cell_value(worksheet[cell])

                if responses and indicator.get('column_year'):
                    cell_year = indicator['column_year'] + str(i + 5)
                    value = '{0} ({1})'.format(value, worksheet[cell_year].value)

                out[country_code][indicator['code']] = value

                # Custom stuff :|

                # 2.4 is handled a bit differently
                if indicator['code'] == '2.4':
                    value = 1 if value >= 1 else value
                    out[country_code][indicator['code']] = value

                # Show all level 2, non derived scores (eg 1.2, 3.4, 5.1)
                # as percentages, rounded to 2 places
                if (indicator['code'].count('.') == 1 and
                        not indicator['code'][-1].isalpha() and
                        value is not None):

                    out[country_code][indicator['code']] = round(
                        value * 100 if value <= 1 else value, 2)
        add_main_scores(out[country_code])
        add_full_score(out[country_code])

    if random_values:
        for code, country in countries.iteritems():
            if country['iso2'] not in country_codes and country['iso2']:
                out[country['iso2']] = OrderedDict()
                for indicator in indicators:
                    if (indicator['level'] <= 2 and
                            not indicator['code'][-1].isalpha()):
                        out[country['iso2']][indicator['code']] = random.randint(
                            0, 100)
    return out


def themes_per_country(prefix=None, random_values=False):
    '''
    Returns a dict containing the values for all themes for all countries,
    with the following structure:

        {
            'CL': {
                    '1A.A': 68.4,
                    '2A': 100.0,
                    '3A': 83.07,
                    # ...
                    },
            'TZ': {
                    '1A.A': 83.25,
                    '2A': 100.0,
                    '3A': 63.18,
                    # ...
                    },

            # ...
        }

    If `prefix` is provided, it will be added at the beginning of the code
    (eg to mix themes and indicators).

    If `random_values` is True, countries not present in the spreadsheet are
    returned with random values.
    '''

    out = OrderedDict()

    themes = get_themes(include_columns=True)
    ws = wb[THEMES_SHEET]
    country_codes = []
    for i in xrange(3, len(ws.rows) + 1):
        country_name = ws['A' + str(i)].value
        if not country_name:
            continue
        country_code = get_country_code(country_name)
        if not country_code:
            print 'Warning: Could not get country code for {0}'.format(
                country_name)
        country_codes.append(country_code)
        out[country_code] = OrderedDict()
    for i, country_code in enumerate(country_codes):
        for theme in themes:
            if theme['level'] == 2 and theme.get('column'):
                cell = theme['column'] + str(i + 4)

                value = get_numeric_cell_value(ws[cell])

                if isinstance(value, basestring):
                    value = None

                key = str(prefix) + theme['code'] if prefix else theme['code']

                if isinstance(value, (long, float)):
                    out[country_code][key] = round(value, 2)
                else:
                    out[country_code][key] = value

    if random_values:
        for code, country in countries.iteritems():
            if country['iso2'] not in country_codes and country['iso2']:
                out[country['iso2']] = OrderedDict()
                for theme in themes:
                    if (theme['level'] == 2):
                        key = (str(prefix) + theme['code'] if prefix
                               else theme['code'])
                        out[country['iso2']][key] = random.randint(
                            0, 100)
    return out


def indicators_as_csv(output_dir=OUTPUT_DIR):
    '''
    Write a CSV file with all indicators, in the form:

        code,title,core,level
        1,Governance,True,1
        1.1,International Framework,True,2
        1.1.1,Is the State party to the United Nations treaties?,True,3

        ...
    '''
    indicators = get_all_indicators()
    output_file = os.path.join(output_dir, 'indicators.csv')

    with open(output_file, 'w') as f:
        w = csv.DictWriter(f, ['code', 'title', 'core', 'level'])
        w.writeheader()
        w.writerows(indicators)


def get_nested_indicators(parent_indicator, all_indicators):
    if parent_indicator['level'] >= 4:
        return
    out = []
    for indicator in all_indicators:
        if (indicator['code'].startswith(parent_indicator['code']) and
                indicator['level'] == parent_indicator['level'] + 1):
            if indicator['level'] < 4:
                nested_indicators = get_nested_indicators(indicator,
                                                          all_indicators)
                if nested_indicators:
                    indicator['children'] = nested_indicators
            out.append(indicator)

    return out


def get_nested_themes(parent_theme, all_themes):
    out = []
    for theme in all_themes:
        numeric_part = ''.join([x for x in theme['code'] if x.isdigit()])
        if (numeric_part == parent_theme['code']
                and theme['level'] == parent_theme['level'] + 1):
            if theme['level'] < 4:
                nested_themes = get_nested_themes(theme,
                                                  all_themes)
                if nested_themes:
                    theme['children'] = nested_themes
            out.append(theme)

    return out


def indicators_as_json(output_dir=OUTPUT_DIR):
    '''
    Write a JSON file with all indicators nested, in the form:

        [
            {
                "code": "1",
                "core": true,
                "level": 1,
                "title": "Governance"
                "children": [
                    {
                        "code": "1.1",
                        "core": true,
                        "level": 2,
                        "title": "International Framework"
                        "children": [
                            {
                                "code": "1.1.1",
                                "core": true,
                                "level": 3,
                                "title": "Is the State party to the United Nations treaties?"
                            }
                        ]
                    }
                ]
            },

            ...
        ]
    '''

    out = []
    indicators = get_all_indicators()
    for indicator in [i for i in indicators if i['level'] == 1]:
        indicator['children'] = get_nested_indicators(indicator, indicators)
        out.append(indicator)

    output_file = os.path.join(output_dir, 'indicators.json')

    with open(output_file, 'w') as f:
        f.write(json.dumps(out))


def themes_as_json(output_dir=OUTPUT_DIR):
    '''
    Write a JSON file with all themes nested, in the form:

        [
            {
                "code": "1",
                "level": 1,
                "title": "Children with Disabilities"
                "children": [
                    {
                        "code": "1.A.A",
                        "level": 2,
                        "title": "Structure and Support"
                        "indicators": [
                            {
                                "code": "1.4.4j",
                                "title": "Is data disaggregated by disability status?"
                            },
                            {
                                "code": "3.2.1j",
                                "title": "Do national laws forbid discrimination in education by disability status?"
                            },
                            ...
                        ]
                    }
                ]
            },

            ...
        ]
    '''

    out = []
    themes = get_themes(only_with_values=True, include_indicators=True)
    for theme in [i for i in themes if i['level'] == 1]:
        theme['children'] = get_nested_themes(theme, themes)
        out.append(theme)

    output_file = os.path.join(output_dir, 'themes.json')

    with open(output_file, 'w') as f:
        f.write(json.dumps(out))


def indicators_per_country_as_json(one_file=True, output_dir=OUTPUT_DIR):

    out = indicators_per_country()
    if one_file:
        output_file = os.path.join(output_dir, 'indicators_per_country.json')

        with open(output_file, 'w') as f:
            f.write(json.dumps(out))
    else:
        for country_code in out.keys():
            output_file = os.path.join(output_dir,
                                       '{0}.json'.format(country_code))

            with open(output_file, 'w') as f:
                f.write(json.dumps(out[country_code]))


def scores_per_country_as_json(output_dir=OUTPUT_DIR, random_values=False):

    out = indicators_per_country(max_level=2, derived=False,
                                 random_values=random_values)
    for country in out.keys():
        add_main_scores(out[country])
        add_full_score(out[country])

    file_name = ('scores_per_country.json' if not random_values
                 else 'scores_per_country_random.json')
    output_file = os.path.join(output_dir, file_name)

    with open(output_file, 'w') as f:
        f.write(json.dumps(out))


def scores_per_country_as_csv(output_dir=OUTPUT_DIR, random_values=False):
    '''
    Write a CSV file with the level 1 and 2 scores for each country, as well as
    the transversal themes, in the form:

        iso2,index,1,1.1,1.2,..,t1.A.A
        CL,68.78,100,56.334,89.322,...,68.4

        ...

    Note that transversal theme codes are prefixed with `t` to avoid conflicts
    '''
    out = indicators_per_country(max_level=2, derived=False,
                                 random_values=random_values)
    themes = themes_per_country(prefix='t', random_values=random_values)

    out_list = []
    for country in out.keys():
        if country in themes:
            out[country].update(themes[country])
        add_main_scores(out[country])
        add_full_score(out[country])
        out[country]['iso2'] = country

        out_list.append(out[country])

    file_name = ('scores_per_country.csv' if not random_values
                 else 'scores_per_country_random.csv')
    output_file = os.path.join(output_dir, file_name)

    with open(output_file, 'w') as f:
        w = csv.DictWriter(f, out_list[0].keys())
        w.writeheader()
        w.writerows(out_list)


def c3_ready_json(output_dir=OUTPUT_DIR, random_values=False):
    '''
    Writes a C3 optimized JSON file to display the country bar charts.

    Contains a list of objects, one for each country. First and second level
    indicators are normalized to fit the total percentage of each category.
    Transversal themes are included rounded to two decimal places.

    [
      {
        "1": 12.85,
        "1.1": 20.0,
        "1.2": 10.0,
        "1.3": 0.0,
        "1.4": 16.88,
        "1.5": 17.39,
        "2": 15.13,
        "2.1": 8.32,
        "2.2": 24.0,
        "2.3": 18.3,
        "2.4": 25.0,
        "index": 72.90,
        "name": "Chile",
        "t1A.A": 68.4,
        "t2A": 100,
        "t3A": 83.07,
        "t3B": 72.03,
        "t4A": 55.53,
        "t5A": 76.14,
        "t6A": 71.1,
        "t7A": 75,
        "t7B": 75.59,
        "t8A": 66.66,
        "t9A": 0
      },
      ...
    ]
    '''

    indicators = indicators_per_country(max_level=2, derived=False,
                                        random_values=random_values)

    themes = themes_per_country(prefix='t', random_values=random_values)

    out = []
    for country_code, values in indicators.iteritems():
        item = OrderedDict()

        # Normalize scores
        scores = {str(n): [] for n in xrange(1, 6)}
        scores['main'] = []
        for code, value in values.iteritems():
            if code == 'index':
                continue
            if '.' not in code:
                scores['main'].append(value)
            else:
                scores[code[:1]].append(value)

        for code, value in values.iteritems():
            if code == 'index':
                continue
            if '.' not in code:
                item[code] = round(value / len(scores['main']), 2)
            else:
                item[code] = round(value / len(scores[code[:1]]), 2)

        # Add Transversal themes
        item.update(themes[country_code])

        # Add full score
        item.update(get_full_score(values))

        # Add country name
        item['name'] = get_country_name(country_code)

        out.append(item)

    file_name = ('c3_scores_per_country.json' if not random_values
                 else 'c3_scores_per_country_random.json')
    output_file = os.path.join(output_dir, file_name)

    with open(output_file, 'w') as f:
        f.write(json.dumps(out))


if __name__ == '__main__':

    description = '''
Builds the data files needed for powering the visualizations for the Right to
Education Index website.

The source of data is an Excel file (xlsx). By default this is assumed to be
at `data/rtei_data_2015.xlsx` but you can provide a different location with the
`-i` flag.

The outputs are JSON files, by default created on the `rtei/static/data`
folder. You can change the destination folder with the `-o` flag.

The available outputs are:

    * `indicators-json`
    * `indicators-csv `
    * `themes-json`
    * `scores-per-country-json`
    * `scores-per-country-csv`
    * `indicators-per-country`
    * `c3-ready-json`
    * `all`
    '''

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('type',
                        help='Output type')
    parser.add_argument('-i', '--input',
                        help='Input Excel (xlsx) file')
    parser.add_argument('-o', '--output',
                        help='Output directory for the files')
    parser.add_argument('-r', '--random',
                        action='store_true',
                        help='Fill values for missing countries with random values')

    args = parser.parse_args()

    input_file = args.input or INPUT_FILE
    output_dir = args.output or OUTPUT_DIR

    wb = load_workbook(input_file, data_only=True)

    with open(COUNTRIES_FILE, 'r') as f:
        countries = json.load(f)
    if args.type == 'all':
        indicators_as_json(output_dir)
        themes_as_json(output_dir)
        indicators_per_country_as_json(one_file=False, output_dir=output_dir)
        scores_per_country_as_json(output_dir, random_values=args.random)
        c3_ready_json(output_dir=output_dir)
    elif args.type == 'indicators-json':
        indicators_as_json(output_dir)
    elif args.type == 'themes-json':
        themes_as_json(output_dir)
    elif args.type == 'indicators-csv':
        indicators_as_csv(output_dir)
    elif args.type == 'scores-per-country-json':
        scores_per_country_as_json(output_dir, random_values=args.random)
    elif args.type == 'scores-per-country-csv':
        scores_per_country_as_csv(output_dir, random_values=args.random)
    elif args.type == 'indicators-per-country':
        indicators_per_country_as_json(one_file=False, output_dir=output_dir)
    elif args.type == 'c3-ready-json':
        c3_ready_json(output_dir=output_dir, random_values=args.random)
    else:
        print 'Unknown output type'
