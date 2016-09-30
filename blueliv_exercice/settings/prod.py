from .base import *


try:
    with open(os.getenv('CONFIG'), 'r') as f:
        CONFIG = json.loads(f.read())
except Exception as e:
    logger.exception(e)
    raise ImproperlyConfigured

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = CONFIG['secret_key']
