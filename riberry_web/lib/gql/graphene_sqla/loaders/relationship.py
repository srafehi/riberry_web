import riberry
from promise import Promise
from promise.dataloader import DataLoader
from sqlalchemy import orm


class RelationshipLoader(DataLoader):

    def __init__(self, target_member, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_cls = target_member.model
        self.target_member = target_member

    def batch_load_fn(self, models):
        ids = {model.id for model in models}
        id_filter = self.source_cls.model.id.in_(ids)
        results = riberry.model.conn.query(self.source_cls.model).filter(id_filter).options(
            orm.joinedload(self.target_member.member),
        ).all()

        mapping = {}
        for result in results:
            value = getattr(result, self.target_member.name)
            if isinstance(value, (list, tuple)):
                mapping[result.id] = riberry.policy.context.filter(value, action='view')
            elif value and riberry.policy.context.authorize(value, action='view'):
                mapping[result.id] = value

        res = [mapping.get(model.id) for model in models]
        return Promise.resolve(res)
