from pathlib import Path

import uvicorn
from fastapi import FastAPI
from starlette.graphql import GraphQLApp
from starlette.staticfiles import StaticFiles

from .lib.gql.schema import schema
from .middleware.auth import RiberryAuthMiddleware
from .middleware.database import RiberryDatabaseMiddleware
from .riberry.policy_context import apply_policy_context_store

apply_policy_context_store()
app = FastAPI()
app.add_middleware(RiberryAuthMiddleware)
app.add_middleware(RiberryDatabaseMiddleware)
module_path = Path(__file__).parent
app.add_route("/gql", GraphQLApp(schema=schema))
app.mount('/', StaticFiles(directory=module_path / 'webapp', html=True), name='static')


def main(host: str = '127.0.0.1', port: int = 5445, log_level: str = 'info', **kwargs):
    uvicorn.run(
        app='riberry_web.app:app' if kwargs.get('reload') else app,
        host=host,
        port=port,
        log_level=log_level,
        **kwargs,
    )
