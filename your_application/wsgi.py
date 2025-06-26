"""
WSGI config for your_application project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app

application = app