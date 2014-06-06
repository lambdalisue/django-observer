try:
    # make_password was introduced from django 1.4
    from django.contrib.auth.hashers import make_password
except ImportError:
    # Copied from django 1.3.7 set_password method
    # https://github.com/django/django/blob/1.3.7/
    # django/contrib/auth/models.py#L255
    def make_password(raw_password):
        from django.contrib.auth.models import get_hexdigest
        import random
        algo = 'sha1'
        salt = get_hexdigest(algo,
                             str(random.random()),
                             str(random.random()))[:5]
        hsh = get_hexdigest(algo, salt, raw_password)
        return '%s$%s$%s' % (algo, salt, hsh)

try:
    # Python 3 have mock in unittest
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

try:
    from django.test.utils import override_settings
except ImportError:
    from override_settings import override_settings

try:
    from unittest import skip
except ImportError:
    from django.utils.unittest import skip


def get_auth_user_model_str():
    # to keep independency, django.conf is used instead of apps.conf
    from django.conf import settings
    return getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

auth_user_model = get_auth_user_model_str()
