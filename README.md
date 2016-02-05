# Right to Education Index (RTEI) website

This site is powered by [Wagtail](https://wagtail.io)


# Setup

* Create a Postgres User and Database:

        sudo -u postgres createuser -S -D -R -P -l rtei
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

## Dump initial data

Dump a new set of initial data:

        cd rtei
        python manage.py dumpdata --natural-foreign --indent=4 -e contenttypes -e auth.Permission -e sessions -e wagtailcore.pagerevision -e auth.user > rtei/fixtures/initial_data.json

Wagtail pages must be owned by an existing user. To ensure a user exists, edit the `rtei/fixtures/initial_data.json` file to include a non-active 'default' user, by adding the following to the file:

        {
            "model": "auth.user",
            "fields": {
                "password": "!HphuMC62NQpkCLQoLhubOt7jLV1SmFPyL4pkiAYu",
                "last_login": null,
                "is_superuser": false,
                "username": "default",
                "first_name": "",
                "last_name": "",
                "email": "",
                "is_staff": false,
                "is_active": false,
                "date_joined": "2016-02-02T13:27:04.190Z",
                "groups": [],
                "user_permissions": []
            }
        },

If new pages have been added to the fixture file, ensure the owner property is `owner: ['default']`.
