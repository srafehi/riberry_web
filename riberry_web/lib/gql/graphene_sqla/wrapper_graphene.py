import graphene
from graphql_relay import to_global_id


def make_connection_type(model_type):
    class Meta:
        node = model_type

    return type(
        f'{model_type.__name__}Connection',
        (graphene.relay.Connection,),
        {'Meta': Meta}
    )


class ModelInterface(graphene.Interface):
    id = graphene.ID(required=True)
    internal_id = graphene.Int(name='internalId', required=True)

    def resolve_id(self, *_):
        return to_global_id(type(self).__name__, str(self.id))

    def resolve_internal_id(self, *_):
        return self.id


class ModelType(graphene.ObjectType, ModelInterface):
    _model = None
    __children__ = {}

    def __init_subclass__(cls, **kwargs):
        result = super().__init_subclass__(**kwargs)
        cls.connection_type = make_connection_type(cls)
        cls.__children__[cls.__name__] = cls

        cls_vars = vars(cls)

        for var in cls_vars:
            if var.startswith('resolve_'):
                var_name = var.replace('resolve_', '', 1)
                if var_name not in cls_vars:
                    raise ValueError(f'{var!r} defined for {cls}, but {var_name!r} was not')

        return result

    @classmethod
    def instance(cls, name):
        return cls.__children__[name]
