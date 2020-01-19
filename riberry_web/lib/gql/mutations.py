import graphene
import riberry


class GetAccessToken(graphene.relay.ClientIDMutation):

    class Input:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    access_token = graphene.Field(graphene.String)

    @classmethod
    def mutate_and_get_payload(cls, *_, **input_data):
        access_token = riberry.services.auth.authenticate_user(
            username=input_data['username'],
            password=input_data['password']
        )
        riberry.model.conn.commit()
        return cls(access_token=access_token)
