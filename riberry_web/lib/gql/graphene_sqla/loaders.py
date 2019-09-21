import datetime
import threading

import graphene
import pendulum
import riberry
from promise import Promise
from promise.dataloader import DataLoader
from sqlalchemy import orm, DateTime

from .fields import PaginationConnectionField
from .wrapper_sqla import SqlaModelMember


class PaginationLoader(DataLoader):

    def __init__(self, target_to_source_member, pagination_details, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_cls = target_to_source_member.model
        self.target_to_source_member = target_to_source_member
        self.details = pagination_details

    def batch_load_fn(self, models):
        return Promise.resolve([self.load_fn(model) for model in models])

    @staticmethod
    def cleanse_value(column, value):
        column_type = column.property.columns[0].type
        if isinstance(column_type, DateTime):
            dt: pendulum.DateTime = pendulum.parse(value)
            return datetime.datetime(
                year=dt.year,
                month=dt.month,
                day=dt.day,
                hour=dt.hour,
                minute=dt.minute,
                second=dt.second,
                microsecond=dt.microsecond,
                tzinfo=dt.timezone,
            )
        return value

    def load_fn(self, model):
        column = getattr(self.target_cls.model, self.details.order_by)
        order = getattr(column, self.details.order) if self.details.order else None

        query = riberry.model.conn.query(
            self.target_cls.model,
        ).join(
            self.target_to_source_member.member,
        ).filter(
            (type(model).id == model.id)
        )

        if self.details.after is not None:
            query = query.filter(column > self.cleanse_value(column, self.details.after))
        if self.details.before is not None:
            query = query.filter(column < self.cleanse_value(column, self.details.before))

        if self.details.first is None and self.details.last is None and order is not None:
            query = query.order_by(order())
        if self.details.first is not None:
            query = query.order_by(column.asc()).limit(self.details.first)
        if self.details.last is not None:
            query = query.order_by(column.desc()).limit(self.details.last)

        return riberry.policy.context.filter(query.all(), action='view')


class PaginationDetails:

    def __init__(self, before, after, first, last, order_by, order):
        self.before = before
        self.after = after
        self.first = first
        self.last = last
        self.order_by = order_by
        self.order = order

    def __hash__(self):
        return hash((
            self.before,
            self.after,
            self.first,
            self.last,
            self.order_by,
            self.order,
        ))

    def __eq__(self, other):
        return type(self) == type(other) and hash(self) == hash(other)


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


class LoaderFactory:
    _enum = {}
    _cache = threading.local()

    @property
    def _factory(self):
        if not hasattr(self._cache, 'factory'):
            self._cache.factory = {}
        return self._cache.factory

    def relationship(self, target_member) -> RelationshipLoader:
        if target_member not in self._factory:
            self._factory[target_member] = RelationshipLoader(target_member=target_member)
        return self._factory[target_member]

    def relationship_resolver(self, target_member):
        def _resolver(self_, *_):
            return self.relationship(target_member).load(self_)

        return _resolver

    def relationship_attribute_resolver(self, model_member: SqlaModelMember):
        cls = graphene.List if model_member.is_list() else graphene.Field
        return cls(lambda: model_member.target.model_type), self.relationship_resolver(model_member)

    @classmethod
    def _make_sortable_enum(cls, target_name, sortable_fields):
        if target_name not in cls._enum:
            cls._enum[target_name] = type(
                f'{target_name}OrderBy',
                (graphene.Enum,),
                sortable_fields,
            )
        return cls._enum[target_name]

    @classmethod
    def _make_order_enum(cls):
        if 'Order' not in cls._enum:
            cls._enum['Order'] = type(
                'Order',
                (graphene.Enum,),
                {'ASC': 'asc', 'DESC': 'desc'},
            )
        return cls._enum['Order']

    def connection_attribute_resolver(self, model_member: SqlaModelMember, sortable_fields=None):

        sortable_fields = sortable_fields or {'INTERNAL_ID': 'id'}
        sortable_field_enum = self._make_sortable_enum(model_member.target.name, sortable_fields)
        order_field_enum = self._make_order_enum()

        attribute = PaginationConnectionField(
            lambda: getattr(model_member.target.model_type(), 'connection_type'),
            order_by=sortable_field_enum(),
            order=order_field_enum(),
        )

        def resolve_attribute(self, _, before=None, after=None, first=None, last=None,
                              order_by=list(sortable_fields.values())[0], order=None):
            after_value = None
            if after:
                _, after_by, after_value = after.split(':', maxsplit=2)

            before_value = None
            if before:
                _, before_by, before_value = before.split(':', maxsplit=2)

            return PaginationLoader(
                target_to_source_member=model_member.target_to_source_member,
                pagination_details=PaginationDetails(
                    before=before_value,
                    after=after_value,
                    first=first,
                    last=last,
                    order_by=order_by,
                    order=order,
                ),
            ).load(self)

        return attribute, resolve_attribute


loader_factory = LoaderFactory()
