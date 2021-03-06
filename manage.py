#!/usr/bin/env python3

import os
import sys


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipes.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        raise ImportError('Django not installed.')
    execute_from_command_line(sys.argv)
