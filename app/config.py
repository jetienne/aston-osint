import os


OPENSANCTIONS_API_KEY = os.environ.get('OPENSANCTIONS_API_KEY', '')
PAPPERS_API_KEY = os.environ.get('PAPPERS_API_KEY', '')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
API_KEY = os.environ.get('API_KEY', '')

HTTP_TIMEOUT = 30.0
HTTP_USER_AGENT = 'aston-osint/0.1.0'
