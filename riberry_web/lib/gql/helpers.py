import graphene

from .graphene_sqla.helpers import non_null_list
from .graphene_sqla.wrapper_graphene import ModelType
from .graphene_sqla.wrapper_sqla import SqlaModel


def create_sqla_query(
        sqla_model,
        query_cls=graphene.ID(),
        query_attribute='internal_id',
        sqla_attribute='id',
        is_list=False,
):
    """ Helper function to create a graphene query for a given SQLA model. """

    cls = non_null_list if is_list else graphene.Field
    attribute = cls(
        lambda: ModelType.instance(SqlaModel(sqla_model).name),
        **{query_attribute: query_cls}
    )

    def resolve(*_, **values):
        query = sqla_model.query().filter(
            getattr(sqla_model, sqla_attribute) == values[query_attribute],
        )

        return query.all() if is_list else query.first()

    return attribute, resolve
