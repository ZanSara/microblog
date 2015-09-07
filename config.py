# -*- coding: utf-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

WTF_CSRF_ENABLED = True
SECRET_KEY = '.ADF\x73m\x21\xc3s\x44c@c\xff..adza}hxd\xd1/\x2f3\x1bvSGy\xdcS\x0f\xd3$'

# mail server settings
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'double.onedoubleninesix'
MAIL_PASSWORD = 'double1996'
#MAIL_DEBUG = True    # Let Flask-Mail becoming verbose on stdout

# administrator list
ADMINS = ['double.onedoubleninesix@gmail.com']

# pagination
POSTS_PER_PAGE = 3


LANGUAGES = {
    'en': 'English',
    'it': 'Italiano'
}
