from contextvars import ContextVar

import riberry
from riberry.policy.store import PolicyContextStore
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class ContextVarPolicyContextStore(PolicyContextStore):
    _store: ContextVar[dict] = ContextVar('store', default=None)

    @property
    def store_dict(self):
        return self._store.get()

    def init(self):
        return self._store.set({'fl': True})

    def get(self, item, default=None):
        if self.store_dict['fl'] and self.store_dict['subject']:
            self.store_dict['fl'] = False
            self.store_dict['subject'] = riberry.model.auth.User.query().filter_by(
                id=self.store_dict['subject'].id).one()
        return self._store.get()[item]

    def set(self, item, value):
        self._store.get()[item] = value

    def reset(self, token):
        self._store.reset(token)


class RiberryAuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        token = riberry.policy.context.store.init()
        try:
            auth(request=request)
            return await call_next(request)
        finally:
            riberry.policy.context.store.reset(token=token)


def auth(request: Request):
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


riberry.policy.context.store = ContextVarPolicyContextStore()
