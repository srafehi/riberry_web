from typing import Optional

from sqlalchemy import Column
from sqlalchemy.orm import RelationshipProperty, ColumnProperty
from sqlalchemy.orm.attributes import InstrumentedAttribute

from .wrapper_graphene import ModelType


class SqlaModel:

    def __init__(self, model):
        self.model = model

    @property
    def name(self):
        return self.model.__name__

    @property
    def model_type(self):
        return ModelType.instance(self.name)

    def member(self, name) -> 'SqlaModelMember':
        return SqlaModelMember(member=getattr(self.model, name), model=self)


class SqlaModelMember:

    def __init__(self, member: InstrumentedAttribute, model: SqlaModel):
        self.member: InstrumentedAttribute = member
        self.model: SqlaModel = model

    @property
    def name(self):
        return self.member.key

    def _sqla_column(self) -> Optional[Column]:
        if isinstance(self.member.prop, ColumnProperty):
            return list(self.member.prop.columns)[0]
        elif isinstance(self.member.prop, RelationshipProperty) and len(self.member.prop.local_columns) == 1:
            return list(self.member.prop.local_columns)[0]

    @property
    def type(self):
        return self._sqla_column().type

    @property
    def nullable(self):
        return self._sqla_column().nullable

    @property
    def default(self):
        return self._sqla_column().default

    @property
    def description(self):
        return self.member.comment

    @property
    def target(self) -> SqlaModel:
        if self.is_relationship():
            return SqlaModel(model=self.member.property.mapper.class_)

    @property
    def target_to_source_member(self) -> 'SqlaModelMember':
        if self.is_relationship() and self.member.property.back_populates:
            return SqlaModelMember(
                member=getattr(self.target.model, self.member.property.back_populates),
                model=self.target
            )

    def is_relationship(self):
        return isinstance(self.member.property, RelationshipProperty)

    def is_list(self):
        return self.member.property.uselist

    def __repr__(self):
        return f'SqlaModelMember(member={self.member})'
