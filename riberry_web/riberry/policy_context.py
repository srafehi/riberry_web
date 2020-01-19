from contextvars import ContextVar

import riberry
from riberry.policy.store import PolicyContextStore


class ContextVarPolicyContextStore(PolicyContextStore):
    _store: ContextVar[dict] = ContextVar('store', default=None)

    @property
    def store_dict(self):
        return self._store.get()

    def init(self):
        return self._store.set({'_first_load': True})

    def get(self, item, default=None):
        if self.store_dict['_first_load'] and self.store_dict['subject']:
            self.store_dict['_first_load'] = False
            self.store_dict['subject'] = riberry.model.auth.User.query().filter_by(
                id=self.store_dict['subject'].id,
            ).one()
        return self._store.get()[item]

    def set(self, item, value):
        self._store.get()[item] = value

    def reset(self, token):
        self._store.reset(token)


def apply_policy_context_store():
    riberry.policy.context.store = ContextVarPolicyContextStore()
