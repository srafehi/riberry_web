from autogqla import Schema

from riberry_web.gql.mutation import Mutation
from riberry_web.gql.query import Query

schema = Schema(query=Query, mutation=Mutation)
