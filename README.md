# Right to Education Index (RTEI) website

[![Build Status](https://travis-ci.org/okfn/rtei.svg?branch=master)](https://travis-ci.org/okfn/rtei)

This site is powered by [Wagtail](https://wagtail.io)


# Setup

* Create a Postgres User and Database:

        sudo -u postgres createuser -d -S -R -P -l rtei
        sudo -u postgres createdb -O rtei rtei -E utf-8

* Create a Virtualenv and clone this repo:

        mkvirtualenv rtei
        mkdir src && cd src
        git clone git@github.com:okfn/rtei.git

* Install requirements:

        cd rtei
        pip install -r requirements.txt

* Set up the database:

        python manage.py migrate

* Create a super user and run the site:

        python manage.py createsuperuser
        python manage.py runserver


# Custom Settings

RTEI requires the following values to be present in the settings file.

```python
# Email to receive contact requests from the form on /about/contact-us/
RTEI_CONTACT_FORM_EMAIL = 'contact_form@example.com'
```

# Notes for development

## Tests

Install the tests requirements:

    pip install -r test-requirements.txt

Run:

    ./manage.py test



## Generate data

The JSON data needed to power the visualizations on the site is built using the `build_data.py` script, which parses the original Excel (xlsx) file located at `data`.

Before running the script you must install its requirements:

    cd rtei
    pip install -r data-requirements.txt

Run `./build_data.py -h` to see all the options available.

Most of the times you will want to:

1. Update `data/rtei_data_2015.xlsx` if necessary
2. Run `./build_data.py all`

The JSON data files are generated in `rtei/static/data` by default. These files are:

* `indicators.json`: Master dictionary that links every indicator code to its title (and level). Indicators are nested, eg:

    ```json
            [
                {
                    "code": "1",
                    "core": true,
                    "children": [
                        {
                            "code": "1.1",
                            "core": true,
                            "children": [
                                {
                                    "code": "1.1.1",
                                    "core": true,
                                    "children": [
                                        {
                                            "code": "1.1.1a",
                                            "core": true,
                                            "level": 4,
                                            "title": "The International Covenant of Economic, Social and Cultural Rights"
                                        },
                                        {
                                            "code": "1.1.1b",
                                            "core": true,
                                            "level": 4,
                                            "title": "The Convention on the Rights of the Child"
                                        },
                                        ...
                                    ]
                                }
                        }
                }
                ...
            ]
    ```

* `themes.json`: Master dictionary that links every theme code to its title (and level). Themes are nested, eg:

    ```json
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
                    }
                ]
            },

            ...
        ]

    ```

* `scores_per_country.json`: Contains all level 1 and 2 scores for all countries, as well as the overall one:


    ```json
            {
                "CL": {
                    "1": 64.76,
                    "1.1": 100.0,
                    "1.2": 50.0,
                    "1.3": 0.0,
                    "1.4": 84.4,
                    "1.6": 89.4,
                    "2": 51.95,
                    "2.1": 33.3,
                    "2.2": 96.0,
                    "2.3": 73.2,
                    "2.4": 5.3,
                    "3": 88.3833,
                    "3.1": 89.6,
                    "3.2": 83.25,
                    "3.3": 92.3,
                    "4": 80.8,
                    "4.1": 68.4,
                    "4.2": 77.7,
                    "4.3": 96.3,
                    "5": 55.4333,
                    "5.1": 66.5,
                    "5.2": 66.5,
                    "5.3": 33.3,
                    "index": 68.2653
                },
                "NG": {
                    "1": 94.56,
                    "1.1": 100.0,
                    "1.2": 100.0,
                    "1.3": 100.0,
                    "1.4": 84.4,
                    "1.6": 88.4,
                    "2": 53.275,
                    "2.1": 25.6,
                    "2.2": 50.0,
                    "2.3": 37.5,
                    "2.4": 100.0,
                    "3": 77.8333,
                    "3.1": 97.4,
                    "3.2": 58.3,
                    "3.3": 77.8,
                    "4": 79.9667,
                    "4.1": 100.0,
                    "4.2": 44.3,
                    "4.3": 95.6,
                    "5": 75.0667,
                    "5.1": 66.5,
                    "5.2": 92.7,
                    "5.3": 66.0,
                    "index": 76.1403
                },

                ...

    ```

* `c3_scores_per_country.json`: C3 optimized data for the country bar charts. Contains all level 1 and 2 scores normalized for all countries, as well as the overall one and the transversal themes:


    ```json
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
    ```

* `{country_code}.json` (eg `CL.json`): For each of the countries available, contains all values for all indicators for that particular country. The values are the user-friendly responses shown on the frontend:


    ```json
            {
                "1": 64.267,
                "1.1": 100.0,
                "1.1.1a": "Yes",
                "1.1.1b": "Yes",
                "1.1.1c": "Yes",
                "1.1.1d": "Yes",
                "1.1.1e": "Yes",
                "1.1.1f": "Yes",
                "1.1.1g": "Yes",
                "1.1.1h": "Yes",
                "1.1.2a": "Yes",
                "1.1.3a": "Yes",
                "1.1.3b": "Yes",
                "1.1.3c": "Yes",
                "1.1.4a": "Yes",
                "1.1.4b": "Yes",
                "1.1.4c": "Yes",
                "1.1.4d": "Yes",
                "1.1.5a": "Not Applicable",
                "1.1.5b": "Not Applicable",
                ...
    ```

### Map data

The map visualizations are powered by a [TopoJSON](https://github.com/mbostock/topojson/wiki) file. This is built using two input files, `data/countries.geojson`, which is constant and does not need to be updated, and `data/scores_per_country.csv`, which needs to be updated:

    ./build_data.py -o data scores-per-country-csv

[Install](https://github.com/mbostock/topojson/wiki/Installation) the `topojson` command (use a version lower than 2.0):

    npm install topojson@1.6.27


This is the full command that needs to be done (note that the output file goes to the `rtei/static/data`):

    topojson -p -o rtei/static/data/countries.topojson --stitch-poles false --id-property iso2 -e data/scores_per_country.csv data/countries.geojson


## Dump Site data

Dump a new set of site data (this is the internal data for managing the site, like pages etc, not the data powering the visualizations):

    cd rtei
    python manage.py dumpdata --natural-foreign --indent=4 -e contenttypes -e auth.Permission -e sessions -e wagtailcore.pagerevision -e auth.user > rtei/fixtures/data.json


## Migrate data on Heroku

Database migrates can be run on heroku against the production settings with:

    heroku run python ./manage.py migrate --settings=rtei.settings.production

## Translations

Translations are managed on [Transifex](https://transifex.com). You will need to install the Transifex command line client:

    pip install transifex-client

If you haven't already done it, you need to create a `~/.transifexrc` file with the following contents:

    [https://www.transifex.com]
    hostname = https://www.transifex.com
    username = YOUR_USERNAME
    password = YOUR_PASSWORD
    token =

To test that it's properly configured, run the following on the repo directory:

    tx status

You should see something along these lines:

    rtei -> rtei (1 of 1)
    Translation Files:
     - en: locale/django.pot (source)
     - ar: locale/ar/LC_MESSAGES/django.po
     - es: locale/es/LC_MESSAGES/django.po
     - fr: locale/fr/LC_MESSAGES/django.po

### Uploading translations to Transifex

New strings added to the source code that need to be translated must be regularly extracted and uploaded to Transifex.

**Note**: This also includes strings in the original data! (eg Indicator titles or responses)

To do so run the following:

    # Extract translatable strings from data
    ./build-data.py translation-strings

    # Extract strings from source code into po files (also keep the master pot file)
    ./manage.py makemessages --keep-pot

    # Upload to Transifex
    tx push -s -t --skip

    #Commit new po files
    git commit -am "Update translation files with new strings"

At this point the strings are available for translation on Transifex.


### Updating translations from Transifex

Once the translators have finished workin on Transifex, update the source code translations with the following commands:

    # Pull strings from Transifex
    tx pull

    # Compile strings catalogue, ie the locale/*.mo files (You need to restart the server after this)
    ./manage compilemessages

    # Commit the changes
    git commit -am "Updated strings from Transifex"

### Rebuilding CSS

The project uses SASS. To install it run:

    sudo gem install sass

To rebuild the CSS, watching for changes in the scss files, run:

    sass rtei/static/scss/rtei.scss:rtei/static/css/rtei.css --watch
