import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

WTF_CSRF_ENABLED = True
SECRET_KEY = '.ADF\x73m\x21\xc3s\x44c@c\xff..adza}hxd\xd1/\x2f3\x1bvSGy\xdcS\x0f\xd3$'

# mail server settings
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = 'niho.zar'
MAIL_PASSWORD = 'nihozar'

# administrator list
ADMINS = ['nihozar@yandex.com']

