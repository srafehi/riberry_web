""" Contains classes to assist in building graphene attributes and connections """

from types import FunctionType
from typing import Optional, Iterable, Union, Tuple

import graphene
import sqlalchemy
from graphene import Scalar, Field, List
from sqlalchemy.ext.declarative import DeclarativeMeta

from .fields import PaginationConnectionField
from .loaders import loader_factory
from .wrapper_sqla import SqlaModel, SqlaModelMember


class Builder:
    """ Single point of entry for building SQLAlchemy-related graphene attributes """

    def __init__(self, model: DeclarativeMeta):
        self.model: SqlaModel = SqlaModel(model=model)

    def field(self, member_name: str, **kwargs) -> Scalar:
        """ Returns a graphene List/Field for the SQLAlchemy member """
        return create_field(self.model.member(name=member_name), **kwargs)

    def relationship(self, member_name: str) -> Tuple[Union[List, Field], FunctionType]:
        """ Returns a graphene relationship for the given SQLAlchemy relationship """
        return loader_factory.relationship_attribute_resolver(self.model.member(name=member_name))

    def connection(self, member_name: str, sortable_fields: Optional[Iterable[str]] = None) -> \
            Tuple[PaginationConnectionField, FunctionType]:
        """ Returns a graphene relay-style connection relationship for the given SQLAlchemy attribute """
        return loader_factory.connection_attribute_resolver(
            model_member=self.model.member(name=member_name),
            sortable_fields=sortable_fields,
        )

    # noinspection PyMethodMayBeStatic
    def proxy(self, model: DeclarativeMeta, is_list: bool, **kwargs) -> Union[List, Field]:
        """ Returns a basic graphense List/Field for a given SQLAlchemy member.

        Used for custom properties and does not delegate to a loader.
        """
        return graphene.List(model, **kwargs) if is_list else graphene.Field(model, **kwargs)


def create_field(model_member: SqlaModelMember, **kwargs) -> Scalar:
    """ Converts a SQLAlchemy member type to a graphene member type"""

    if isinstance(model_member.type, sqlalchemy.String):
        cls = graphene.String
    elif isinstance(model_member.type, sqlalchemy.Integer):
        cls = graphene.Int
    elif isinstance(model_member.type, sqlalchemy.DateTime):
        cls = graphene.DateTime
    elif isinstance(model_member.type, sqlalchemy.Boolean):
        cls = graphene.Boolean
    elif isinstance(model_member.type, sqlalchemy.JSON):
        cls = graphene.JSONString
    elif isinstance(model_member.type, sqlalchemy.Binary):
        cls = graphene.String
    else:
        raise Exception(f'{model_member.type} {type(model_member.type)}')

    return cls(description=model_member.description, **kwargs)
