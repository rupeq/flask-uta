import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "b'wv\xc8Qu\x1b\xd5\x91\x9e\xb5\xb9\xf5J2\xbbq'"
    MONGODB_SETTINGS = { 'db' : 'MRC_Enrollment' }

