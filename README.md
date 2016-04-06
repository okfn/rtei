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

* `indicators.json`: Master dictionary that links every indicator code to its title (and level):

    ```json
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
                    "title": "Is the State party to the following United Nations treaties?"
                },
                ...
            }
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

* `{country_code}.json` (eg `CL.json`): For each of the countries available, contains all values for all indicators for that particular country:


    ```json
            {
                "1": 64.76,
                "1.1": 100.0,
                "1.1.1a": 1,
                "1.1.1b": 1,
                "1.1.1c": 1,
                "1.1.1d": 1,
                "1.1.1e": 1,
                "1.1.1f": 1,
                "1.1.1g": 1,
                "1.1.1h": 1,
                "1.1.2a": 1,
                "1.1.3a": 1,
                "1.1.3b": 1,
                "1.1.3c": 1,
                "1.1.4a": 1,
                "1.1.4b": 1,
                "1.1.4c": 1,
                "1.1.4d": 1,
                "1.1.5a": null,
                "1.1.5b": null,
                "1.1.5c": null,

                ...
    ```

### Map data

The map visualizations are powered by a [TopoJSON](https://github.com/mbostock/topojson/wiki) file. This is built using two input files, `data/countries.geojson`, which is constant and does not need to be updated, and `data/scores_per_country.csv`, which needs to be updated:

    ./build_data.py -o data scores-per-country-csv

After [installing](https://github.com/mbostock/topojson/wiki/Installation) the `topojson` command, this is the full command that needs to be done (note that the output file goes to the `rtei/static/data`):

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

To do so run the following:

    # Extract strings from source code into po files (also keep the master pot file)
    ./manage.py makemessages --keep-pot

    # Upload to Transifex
    tx push -s -t

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
