from pathlib import Path

from fastapi import FastAPI
from starlette.graphql import GraphQLApp
from starlette.staticfiles import StaticFiles

from .lib.gql.schema import schema
from .middleware.auth import RiberryAuthMiddleware

app = FastAPI()
app.add_middleware(RiberryAuthMiddleware)
module_path = Path(__file__).parent
app.add_route("/gql", GraphQLApp(schema=schema))
app.mount('/', StaticFiles(directory=module_path / 'webapp', html=True), name='static')
