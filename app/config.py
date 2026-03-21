import os


OPENSANCTIONS_API_KEY = os.environ.get('OPENSANCTIONS_API_KEY', '').strip()
PAPPERS_API_KEY = os.environ.get('PAPPERS_API_KEY', '').strip()
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '').strip()
API_KEY = os.environ.get('API_KEY', '').strip()

HTTP_TIMEOUT = 30.0
HTTP_USER_AGENT = 'aston-osint/0.1.0'
