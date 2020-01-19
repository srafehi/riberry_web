import graphene
import riberry

from .objects import Query, Mutation


class RiberrySchema(graphene.Schema):

    def execute(self, *args, **kwargs):
        with riberry.model.conn:
            return super().execute(*args, **kwargs)


schema = RiberrySchema(query=Query, mutation=Mutation)
