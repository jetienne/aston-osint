from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.orchestrator import ADAPTERS, run_scan

app = FastAPI(title='Aston OSINT', version='0.1.0')


class ScanRequest(BaseModel):
    name: str
    nationality: str | None = None
    company: str | None = None
    hints: str | None = None


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.get('/api/v1/status')
def status():
    return {
        'service': 'aston-osint',
        'version': '0.1.0',
        'adapters': [
            {'name': a.name, 'available': True}
            for a in ADAPTERS
        ],
    }


@app.post('/api/v1/scan')
async def scan(request: ScanRequest):
    if not request.name.strip():
        raise HTTPException(status_code=400, detail='name is required')

    kwargs = {}
    if request.nationality:
        kwargs['nationality'] = request.nationality
    if request.company:
        kwargs['company'] = request.company

    result = await run_scan(request.name.strip(), **kwargs)
    return result
