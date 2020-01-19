import riberry
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class RiberryAuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        token = riberry.policy.context.store.init()
        try:
            self.auth(request=request)
            return await call_next(request)
        finally:
            riberry.policy.context.store.reset(token=token)

    @staticmethod
    def auth(request: Request):
        """ Sets the current Riberry policy context """

        user = None
        if 'token' in request.cookies:
            token = request.cookies['token']
            try:
                payload = riberry.model.auth.AuthToken.verify(token)
                user = riberry.model.auth.User.query().filter_by(username=payload['subject']).one()
            except Exception:
                raise

        riberry.policy.context.configure(
            subject=user,
            environment=None,
            policy_engine=riberry.config.config.policies.provider
        )

        return user
