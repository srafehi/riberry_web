from sqlalchemy.orm import RelationshipProperty
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

    @property
    def type(self):
        return self.member.prop.columns[0].type

    @property
    def description(self):
        return self.member.comment

    @property
    def target(self) -> SqlaModel:
        if self.is_relationship():
            return SqlaModel(model=self.member.property.mapper.class_)

    @property
    def target_to_source_member(self) -> 'SqlaModelMember':
        if self.is_relationship():
            return SqlaModelMember(
                member=getattr(self.target.model, self.member.property.back_populates),
                model=self.target
            )

    def is_relationship(self):
        return isinstance(self.member.property, RelationshipProperty)

    def is_list(self):
        return self.member.property.uselist
