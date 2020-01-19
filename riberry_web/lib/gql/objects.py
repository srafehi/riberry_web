import graphene
import riberry

from . import mutations, models, helpers


class Mutation(graphene.ObjectType):
    get_access_token = mutations.GetAccessToken.Field()


class Query(graphene.ObjectType):
    node = graphene.Node.Field()
    all_applications = helpers.non_null_list(lambda: models.Application)
    all_forms = helpers.non_null_list(lambda: models.Form)
    self = graphene.Field(lambda: models.User)

    application, resolve_application = helpers.create_sqla_query(
        sqla_model=riberry.model.application.Application,
        query_attribute='internal_id',
        sqla_attribute='id',
        is_list=False,
    )

    application_by_internal_name, resolve_application_by_internal_name = helpers.create_sqla_query(
        sqla_model=riberry.model.application.Application,
        query_attribute='internal_name',
        sqla_attribute='internal_name',
        is_list=False,
    )

    form, resolve_form = helpers.create_sqla_query(
        sqla_model=riberry.model.interface.Form,
        query_attribute='internal_id',
        sqla_attribute='id',
        is_list=False,
    )

    form_by_internal_name, resolve_form_by_internal_name = helpers.create_sqla_query(
        sqla_model=riberry.model.interface.Form,
        query_attribute='internal_name',
        sqla_attribute='internal_name',
        is_list=False,
    )

    user, resolve_user = helpers.create_sqla_query(
        sqla_model=riberry.model.auth.User,
        query_attribute='user_name',
        sqla_attribute='username',
        is_list=False,
    )

    job, resolve_job = helpers.create_sqla_query(
        sqla_model=riberry.model.job.Job,
        query_attribute='internal_id',
        sqla_attribute='id',
        is_list=False,
    )

    job_execution, resolve_job_execution = helpers.create_sqla_query(
        sqla_model=riberry.model.job.JobExecution,
        query_attribute='internal_id',
        sqla_attribute='id',
        is_list=False,
    )

    @staticmethod
    def resolve_all_applications(*_):
        collection = riberry.model.application.Application.query().all()
        return riberry.policy.context.filter(collection, action='view')

    @staticmethod
    def resolve_all_forms(*_):
        collection = riberry.model.interface.Form.query().all()
        return riberry.policy.context.filter(collection, action='view')

    @staticmethod
    def resolve_self(*_):
        return riberry.policy.context.subject
