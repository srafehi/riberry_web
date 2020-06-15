from contextvars import ContextVar

import riberry
from riberry.policy.store import PolicyContextStore


class ContextVarPolicyContextStore(PolicyContextStore):
    _store: ContextVar[dict] = ContextVar('store', default=None)
    __DEFAULT = {'enabled': False}

    @property
    def store_dict(self):
        return self._store.get()

    def init(self):
        return self._store.set(dict(self.__DEFAULT))

    def get(self, item, default=None):
        return (self._store.get() or self.__DEFAULT)[item]

    def set(self, item, value):
        self._store.get()[item] = value

    def reset(self, token):
        self._store.reset(token)


def apply_policy_context_store():
    riberry.policy.context.store = ContextVarPolicyContextStore()
