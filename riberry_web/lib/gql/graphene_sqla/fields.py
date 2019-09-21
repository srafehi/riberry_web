import graphene


class PaginationConnectionField(graphene.relay.ConnectionField):

    @classmethod
    def resolve_connection(cls, connection_type, args, resolved):
        connection_type = connection_type
        edge_type = connection_type.Edge
        pageinfo_type = graphene.PageInfo
        attr_order_by = args.get('order_by') or 'id'
        attr_order = args.get('order')

        edges = [
            edge_type(
                node=node,
                cursor=f'{type(node).__name__}:{attr_order_by}:{getattr(node, attr_order_by)}:{attr_order}'
            )
            for i, node in enumerate(resolved)
        ]

        first_edge_cursor = edges[0].cursor if edges else None
        last_edge_cursor = edges[-1].cursor if edges else None

        return connection_type(
            edges=edges,
            page_info=pageinfo_type(
                start_cursor=first_edge_cursor,
                end_cursor=last_edge_cursor,
            )
        )
