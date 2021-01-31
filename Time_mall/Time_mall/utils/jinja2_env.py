from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse

def jinja2_env(**options):
    env = Environment(**options)
    env.globals.update({
        "static": staticfiles_storage.url,#保证模板渲染中{{static ('') }}
        "url": reverse #保证模板渲染中{{ url('') }}
    })
    return env