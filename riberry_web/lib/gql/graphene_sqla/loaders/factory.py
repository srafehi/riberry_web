import threading

import graphene

from .pagination import PaginationLoader, PaginationDetails
from .relationship import RelationshipLoader
from ..fields import PaginationConnectionField
from ..helpers import non_null_list
from ..wrapper_sqla import SqlaModelMember


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

    def relationship_attribute_resolver(self, model_member: SqlaModelMember, **kwargs):
        if model_member.is_list():
            attribute = non_null_list(lambda: model_member.target.model_type, **kwargs)
        else:
            options = {
                'required': not model_member.nullable,
                **kwargs,
            }
            attribute = graphene.Field(lambda: model_member.target.model_type, **options)

        return attribute, self.relationship_resolver(model_member)

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
        default_order_by = list(sortable_fields.values())[0]

        attribute = PaginationConnectionField(
            lambda: getattr(model_member.target.model_type(), 'connection_type'),
            order_by=sortable_field_enum(),
            required=True,
        )

        def resolve_attribute(
                self_,
                _,
                before=None,
                after=None,
                first=None,
                last=None,
                order_by=default_order_by,
        ):
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
                ),
            ).load(self_)

        return attribute, resolve_attribute
