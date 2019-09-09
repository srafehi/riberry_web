import uvicorn
from . import app


def main(host='127.0.0.1', port=5445, log_level='info', **kwargs):
    uvicorn.run(app.app, host=host, port=port, log_level=log_level, **kwargs)
