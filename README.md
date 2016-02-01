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
