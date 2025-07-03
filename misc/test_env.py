#!/usr/bin/env python
"""Test if environment variables are being loaded from .env.development"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print(f"Current directory: {os.getcwd()}")
print(f"Looking for .env files in: {os.getcwd()}")
print(f"Files found: {[f for f in os.listdir('.') if f.startswith('.env')]}")

# Check environment variable directly
print(f"\nDirect env check:")
print(f"HEALTHIE_API_KEY from os.environ: {os.getenv('HEALTHIE_API_KEY', 'NOT FOUND')}")

# Now check through pydantic settings
from healthie_mcp.config import get_settings

try:
    settings = get_settings()
    print(f"\nPydantic settings check:")
    print(f"HEALTHIE_API_KEY: {'Set' if settings.healthie_api_key else 'Not Set'}")
    print(f"API URL: {settings.healthie_api_url}")
    print(f"Schema dir: {settings.schema_dir}")
    print(f"Cache enabled: {settings.cache_enabled}")
    
    if settings.healthie_api_key:
        print(f"Key starts with: {settings.healthie_api_key[:10]}...")
        print(f"Key length: {len(settings.healthie_api_key)}")
except Exception as e:
    print(f"Error loading settings: {e}")

# Try to manually load .env.development
print(f"\n.env.development file content check:")
env_file = ".env.development"
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('HEALTHIE_API_KEY'):
                print(f"Found in file: {line.strip()[:30]}...")
else:
    print(f"File {env_file} not found!")