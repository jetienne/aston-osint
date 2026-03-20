from fastapi import FastAPI

app = FastAPI(title='Aston OSINT', version='0.1.0')


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.get('/api/v1/status')
def status():
    return {'service': 'aston-osint', 'version': '0.1.0'}
