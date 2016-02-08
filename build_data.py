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
from collections import OrderedDict

from openpyxl import load_workbook

INPUT_FILE = 'data/rtei_data_2015.xlsx'
COUNTRIES_FILE = 'data/countries.json'
OUTPUT_DIR = 'rtei/static/data'

CORE_SHEET = 'Core Questionnaire'
COMPANION_SHEET = 'Companion Questionnaire'

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

    for country in countries:
        if (country_name == country['name'] or
           country_name == country.get('other_names')):
            return country[code_type]
    return None


def get_numeric_cell_value(cell):
    '''
    Return a numeric value rounded to 4 places if it is a float, or the value
    otherwise
    '''
    if isinstance(cell.value, float):
        return round(cell.value, 4)
    else:
        return cell.value


def parse_cell(value):
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
            if cell.value:
                    code, title, level = parse_cell(cell.value)
                    if not code or code in codes_done:
                        continue

                    indicator = {
                        'code': code,
                        'title': title,
                        'core': core,
                        'level': level
                    }
                    if i == 3 and include_columns:
                        indicator['column'] = cell.column

                    codes_done.append(code)
                    out.append(indicator)
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


def add_main_scores(country_indicators):
    '''
    Add the values for the level 1 indicators (ie 1, 2, 3, 4 and 5)

    These are computed with the average of all level 2 indicators (eg 1.1,
    1.2, etc). These are returned as a percentage rounded to 4 decimal
    places.
    '''

    scores = {}
    for code, value in country_indicators.iteritems():
        if code == 'index':
            continue

        if code[:1] not in scores:
            scores[code[:1]] = []

        if code.count('.') == 1 and not code[-1].isalpha():
            scores[code[:1]].append(value * 100 if value <= 1 else value)

    for score, values in scores.iteritems():
        country_indicators[score] = round(sum(values) / len(values), 4)


def add_full_score(country_indicators):
    '''
    Adds the full overall score to the country indicators with the `index` key.

    It is computed with the average of all level 1 indicators (ie 1, 2, 3, 4
    and 5) returned as a percentage rounded to 4 decimal places.
    '''

    values = [country_indicators[str(code)] for code in xrange(1, 6)]
    country_indicators['index'] = round(sum(values) / len(values), 4)


def indicators_per_country(max_level=4, derived=True):
    '''
    Returns a dict containing the values for all indicators for all countries,
    with the following structure:

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
    '''

    out = OrderedDict()

    indicators = get_all_indicators(include_columns=True)

    ws_core = wb[CORE_SHEET]
    ws_companion = wb[COMPANION_SHEET]
    country_codes = []
    for i in xrange(5, len(ws_core.rows)):
        country_name = ws_core['A' + str(i)].value
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
                cell = indicator['column'] + str(i + 5)
                if indicator['core']:
                    value = get_numeric_cell_value(ws_core[cell])
                else:
                    value = get_numeric_cell_value(ws_companion[cell])

                out[country_code][indicator['code']] = value

                # Custom stuff :|

                # 2.4 is handled a bit differently
                if indicator['code'] == '2.4':
                    out[country_code][indicator['code']] = (1 if value >= 1
                                                            else value)

                # Show all level 2, non derived scores (eg 1.2, 3.4, 5.1)
                # as percentages, rounded to 3 places
                if (indicator['code'].count('.') == 1 and
                        not indicator['code'][-1].isalpha()):

                    out[country_code][indicator['code']] = round(
                        value * 100 if value <= 1 else value, 3)

        add_main_scores(out[country_code])
        add_full_score(out[country_code])

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


def indicators_as_json(output_dir=OUTPUT_DIR):
    '''
    Write a JSON file with all indicators, in the form:

        {
            "1": {
                "core": true,
                "level": 1,
                "title": "Governance"
            },
            "1.1": {
                "core": true,
                "level": 2,
                "title": "International Framework"
            },
            "1.1.1": {
                "core": true,
                "level": 3,
                "title": "Is the State party to the United Nations treaties?"
            },

            ...

    '''

    out = OrderedDict()
    for indicator in get_all_indicators():
        code = indicator.pop('code')
        out[code] = indicator

    output_file = os.path.join(output_dir, 'indicators.json')

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


def scores_per_country_as_json(output_dir=OUTPUT_DIR):

    out = indicators_per_country(max_level=2, derived=False)
    for country in out.keys():
        add_main_scores(out[country])
        add_full_score(out[country])

    output_file = os.path.join(output_dir, 'scores_per_country.json')

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
    * `scores-per-country`
    * `indicators-per-country`
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

    args = parser.parse_args()

    input_file = args.input or INPUT_FILE
    output_dir = args.output or OUTPUT_DIR

    wb = load_workbook(input_file, data_only=True)

    with open(COUNTRIES_FILE, 'r') as f:
        countries = json.load(f)

    if args.type == 'all':
        indicators_as_json(output_dir)
        indicators_per_country_as_json(one_file=False, output_dir=output_dir)
        scores_per_country_as_json(output_dir)
    elif args.type == 'indicators-json':
        indicators_as_json(output_dir)
    elif args.type == 'indicators-csv':
        indicators_as_csv(output_dir)
    elif args.type == 'scores-per-country':
        scores_per_country_as_json(output_dir)
    elif args.type == 'indicators-per-country':
        indicators_per_country_as_json(one_file=False, output_dir=output_dir)
