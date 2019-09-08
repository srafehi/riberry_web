import uvicorn
from riberry_web import app


if __name__ == '__main__':
    uvicorn.run(app.app, host='127.0.0.1', port=8000, log_level='info')
