from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse

def jinja2_environment(**options):
    """
    确保可以使用模板引擎中的{{ url('') }} {{ static('') }}这类语句
    """
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
    })
    return env