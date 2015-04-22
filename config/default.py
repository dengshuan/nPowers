import os
BASE_DIR = os.path.abspath(os.path.curdir)
UPLOAD_DIR = os.path.join(BASE_DIR, 'nPowers/static/uploads')
CACHE_TYPE = 'simple'
CSRF_ENABLED = True
CSRF_SESSION_KEY = True
BCRYPT_LOG_ROUNDS = 10
del os
