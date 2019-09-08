from pathlib import Path

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

app = FastAPI()
module_path = Path(__file__).parent
app.mount('/', StaticFiles(directory=module_path / 'webapp', html=True), name='static')
