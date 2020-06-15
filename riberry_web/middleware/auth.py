import riberry
from fastapi import HTTPException, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from http import HTTPStatus


class RiberryAuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        token = riberry.policy.context.store.init()
        try:
            self.auth(request=request)
            return await call_next(request)
        except HTTPException as exc:
            return Response(status_code=exc.status_code)
        finally:
            riberry.policy.context.store.reset(token=token)

    @staticmethod
    def auth(request: Request):
        """ Sets the current Riberry policy context """

        user = riberry.model.auth.User()
        if request.cookies.get('token'):
            token = request.cookies['token']
            try:
                user = riberry.model.auth.UserToken.from_api_key(api_key=token).user
            except riberry.exc.InvalidApiKeyError:
                raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED.value, detail=HTTPStatus.UNAUTHORIZED.phrase)

        riberry.policy.context.configure(subject=user, environment=None)
        return user
