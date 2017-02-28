from .base import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ytschedule',
        'USER': 'ytschedule',
        'PASSWORD': 'ytschedule',
        'HOST': 'localhost',
        'PORT': '',
        'OPTIONS': {
          'sql_mode': 'TRADITIONAL',
           'charset': 'utf8',
           'init_command': 'SET '
              'storage_engine=INNODB,'
              'character_set_connection=utf8,'
              'collation_connection=utf8_bin'
        }
    }
}
