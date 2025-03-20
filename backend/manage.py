#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Al inicio de manage.py, antes de django.setup()
import string
import django.utils

if not hasattr(django.utils, 'baseconv'):
    class BaseConv:
        @staticmethod
        def b62_encode(num, alphabet=string.digits + string.ascii_letters):
            if num == 0:
                return alphabet[0]
            arr = []
            base = len(alphabet)
            while num:
                num, rem = divmod(num, base)
                arr.append(alphabet[rem])
            arr.reverse()
            return ''.join(arr)

        @staticmethod
        def b62_decode(s, alphabet=string.digits + string.ascii_letters):
            base = len(alphabet)
            num = 0
            strlen = len(s)
            for idx, char in enumerate(s):
                power = strlen - (idx + 1)
                num += alphabet.index(char) * (base ** power)
            return num

    django.utils.baseconv = BaseConv


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SolDega.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
