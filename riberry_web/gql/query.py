import graphene
import riberry
from autogqla import make_relationship_resolver, make_relationship_field, make_pagination_field, make_pagination_resolver


class Query(graphene.ObjectType):
    applications = make_relationship_field(riberry.model.application.Application)
    resolve_applications = make_relationship_resolver(riberry.model.application.Application)

    application_instances = make_relationship_field(riberry.model.application.ApplicationInstance)
    resolve_application_instances = make_relationship_resolver(riberry.model.application.ApplicationInstance)

    forms = make_relationship_field(riberry.model.interface.Form)
    resolve_forms = make_relationship_resolver(riberry.model.interface.Form)

    jobs = make_relationship_field(riberry.model.job.Job)
    resolve_jobs = make_relationship_resolver(riberry.model.job.Job)

    job_executions = make_relationship_field(riberry.model.job.JobExecution)
    resolve_job_executions = make_relationship_resolver(riberry.model.job.JobExecution)

    paginate_forms = make_pagination_field(riberry.model.interface.Form)
    resolve_paginate_forms = make_pagination_resolver(riberry.model.interface.Form)

    paginate_job_executions = make_pagination_field(riberry.model.job.JobExecution)
    resolve_paginate_job_executions = make_pagination_resolver(riberry.model.job.JobExecution)
