""" Contains classes to assist in building graphene attributes and connections """

from types import FunctionType
from typing import Optional, Iterable, Union, Tuple, Callable, Any

import graphene
import sqlalchemy
from sqlalchemy.ext.declarative import DeclarativeMeta

from .fields import PaginationConnectionField
from .helpers import non_null_list
from .loaders import loader_factory
from .wrapper_sqla import SqlaModel, SqlaModelMember


class Builder:
    """ Single point of entry for building SQLAlchemy-related graphene attributes """

    field_mapping = mapping = {
        sqlalchemy.String: graphene.String,
        sqlalchemy.Integer: graphene.Int,
        sqlalchemy.Float: graphene.Float,
        sqlalchemy.DateTime: graphene.DateTime,
        sqlalchemy.Boolean: graphene.Boolean,
        sqlalchemy.JSON: graphene.JSONString,
        sqlalchemy.Binary: graphene.String,
        sqlalchemy.Enum: graphene.String,
    }

    def __init__(self, model: DeclarativeMeta):
        self.model: SqlaModel = SqlaModel(model=model)

    def field(self, member_name: str, **kwargs) -> graphene.Scalar:
        """ Returns a graphene List/Field for the SQLAlchemy member """
        return self._create_field(self.model.member(name=member_name), **kwargs)

    def field_with_resolver(
            self,
            member_name: str,
            transformer: Optional[Callable[[Any], Any]] = None,
            **kwargs,
    ) -> Tuple[Any, Any]:
        return (
            self.field(member_name, **kwargs),
            self.resolver(member_name, transformer or (lambda _: _))
        )

    @staticmethod
    def resolver(member_name: str, transformer: FunctionType) -> FunctionType:
        return lambda instance, *_: transformer(getattr(instance, member_name))

    def relationship(self, member_name: str, **kwargs) -> Tuple[Union[graphene.List, graphene.Field], FunctionType]:
        """ Returns a graphene relationship for the given SQLAlchemy relationship """
        return loader_factory.relationship_attribute_resolver(self.model.member(name=member_name), **kwargs)

    def connection(self, member_name: str, sortable_fields: Optional[Iterable[str]] = None) -> \
            Tuple[PaginationConnectionField, FunctionType]:
        """ Returns a graphene relay-style connection relationship for the given SQLAlchemy attribute """
        return loader_factory.connection_attribute_resolver(
            model_member=self.model.member(name=member_name),
            sortable_fields=sortable_fields,
        )

    # noinspection PyMethodMayBeStatic
    def proxy(self, model: DeclarativeMeta, is_list: bool, **kwargs) -> Union[graphene.List, graphene.Field]:
        """ Returns a basic graphene List/Field for a given SQLAlchemy member.

        Used for custom properties and does not delegate to a loader.
        """
        return non_null_list(model, **kwargs) if is_list else graphene.Field(model, **kwargs)

    @classmethod
    def _create_field(cls, model_member: SqlaModelMember, **kwargs) -> graphene.Scalar:
        """ Converts a SQLAlchemy member type to a graphene member type"""

        try:
            sqla_cls = cls.field_mapping[type(model_member.type)]
        except KeyError:
            raise KeyError(f'Unsupported type {type(model_member.type)} from {model_member}')
        else:
            return sqla_cls(description=model_member.description, **{
                'required': not model_member.nullable,
                'default_value': model_member.default,
                **kwargs,
            })
