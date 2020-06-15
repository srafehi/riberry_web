from datetime import timedelta

import graphene
import riberry


class CreateJob(graphene.relay.ClientIDMutation):
    class Input:
        form_internal_name = graphene.String(required=True)
        job_name = graphene.String(required=True)
        execute = graphene.Boolean(default=True)
        input_data = graphene.JSONString()

    success = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(cls, *_, form_internal_name, job_name, execute, input_data):
        riberry.services.job.create_job(
            form=form_internal_name,
            job_name=job_name,
            execute_on_creation=execute,
            input_data=input_data,
        )
        riberry.model.conn.commit()
        return cls(success=True)


class CreateSessionApiKey(graphene.relay.ClientIDMutation):
    class Input:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    api_key = graphene.Field(graphene.String)

    @classmethod
    def mutate_and_get_payload(cls, *_, **input_data):
        user = riberry.model.auth.User.authenticate(username=input_data['username'], password=input_data['password'])
        user_token = riberry.model.auth.UserToken.create(user, type='session', expiry_delta=timedelta(days=5))
        api_key = user_token.generate_api_key()
        riberry.model.conn.add(user_token)
        riberry.model.conn.commit()
        return cls(api_key=api_key)


class Mutation(graphene.ObjectType):
    create_job = CreateJob.Field()
    create_session_api_key = CreateSessionApiKey.Field()
