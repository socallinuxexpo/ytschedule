"""
Do do login/initate oauth.
Use to create/refresh/check authentication.
"""
import sys, os
import time, pytz
import logging
import datetime
import django
from room.models import *

def run():
    response = YouTube.get_authenticated_service(init=True)
