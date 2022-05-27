"""Core Cache Manager App Settings
"""
import os
from django.conf import settings

if not settings.configured:
    settings.configure()
