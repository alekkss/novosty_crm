#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.
Entry point for all Django management commands.
"""

import os
import sys
from pathlib import Path


def main() -> None:
    """
    Run administrative tasks.
    Sets up Django environment and executes management commands.
    """
    # Set the default Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
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
