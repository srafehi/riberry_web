import graphene

from .objects import Query, Mutation

schema = graphene.Schema(query=Query, mutation=Mutation)
