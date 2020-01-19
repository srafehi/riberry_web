import graphene


def non_null_list(*args, **kwargs):
    return graphene.NonNull(graphene.List(graphene.NonNull(*args, **kwargs)))
