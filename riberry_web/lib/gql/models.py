import graphene
import riberry

from .graphene_sqla.builder import Builder
from .graphene_sqla.wrapper_graphene import ModelType


class Application(ModelType):
    build = Builder(riberry.model.application.Application)

    name = build.field('name')
    internal_name = build.field('internal_name')
    description = build.field('description')
    instances, resolve_instances = build.relationship('instances')
    forms, resolve_forms = build.relationship('forms')


class ApplicationInstance(ModelType):
    build = Builder(riberry.model.application.ApplicationInstance)

    name = build.field('name')
    internal_name = build.field('internal_name')

    heartbeat, resolve_heartbeat = build.relationship('heartbeat')
    schedules, resolve_schedules = build.relationship('schedules')
    application, resolve_application = build.relationship('application')
    forms, resolve_forms = build.relationship('forms')

    status = graphene.String()


class ApplicationInstanceSchedule(ModelType):
    build = Builder(riberry.model.application.ApplicationInstanceSchedule)

    days = build.field('days')
    start_time = build.field('start_time')
    end_time = build.field('end_time')
    timezone = build.field('timezone', name='timeZone')
    parameter = build.field('parameter')
    value = build.field('value')
    priority = build.field('priority')

    instance, resolve_instance = build.relationship('instance')


class Heartbeat(ModelType):
    build = Builder(riberry.model.application.Heartbeat)

    created = build.field('created')
    updated = build.field('updated')

    instance, resolve_instance = build.relationship('instance')


class Form(ModelType):
    build = Builder(riberry.model.interface.Form)

    name = build.field('name')
    internal_name = build.field('internal_name')
    description = build.field('description')
    version = build.field('version')

    instance, resolve_instance = build.relationship('instance')
    application, resolve_application = build.relationship('application')
    jobs, resolve_jobs = build.connection('jobs', sortable_fields={
        'INTERNAL_ID': 'id',
        'NAME': 'name',
        'CREATED': 'created',
    })

    input_value_definitions, resolve_input_value_definitions = build.relationship('input_value_definitions')
    input_file_definitions, resolve_input_file_definitions = build.relationship('input_file_definitions')

    document, resolve_document = build.relationship('document')
    groups = build.proxy(lambda: Group, is_list=True)


def simple_resolver(member, transformer=None):
    transformer = transformer or (lambda f: f)
    return lambda instance, *_: transformer(getattr(instance, member))


class Document(ModelType):
    build = Builder(riberry.model.misc.Document)

    type, resolve_type = build.field('type'), simple_resolver('type')
    content, resolve_content = build.field('content'), simple_resolver('content', lambda c: (
        c.decode() if c else None
    ))


class Group(ModelType):
    build = Builder(riberry.model.group.Group)

    name = build.field('name')


class InputValueDefinition(ModelType):
    build = Builder(riberry.model.interface.InputValueDefinition)

    name = build.field('name')
    internal_name = build.field('internal_name')
    description = build.field('description')
    type, resolve_type = build.field('type'), simple_resolver('type')
    required = build.field('required')

    default_value = graphene.JSONString()
    allowed_values = graphene.List(graphene.JSONString)


class InputFileDefinition(ModelType):
    build = Builder(riberry.model.interface.InputFileDefinition)

    name = build.field('name')
    internal_name = build.field('internal_name')
    description = build.field('description')
    type, resolve_type = build.field('type'), simple_resolver('type')
    accept = build.field('accept')
    required = build.field('required')


class Job(ModelType):
    build = Builder(riberry.model.job.Job)

    name = build.field('name')
    created = build.field('created')

    form, resolve_form = build.relationship('form')
    creator, resolve_creator = build.relationship('creator')
    executions, resolve_executions = build.connection('executions', sortable_fields={
        'INTERNAL_ID': 'id',
        'CREATED': 'created',
        'UPDATED': 'updated',
    })


class JobExecution(ModelType):
    build = Builder(riberry.model.job.JobExecution)

    status = build.field('status')
    created = build.field('created')
    started = build.field('started')
    updated = build.field('updated')
    completed = build.field('completed')
    priority = build.field('priority')

    creator, resolve_creator = build.relationship('creator')
    job, resolve_job = build.relationship('job')
    streams, resolve_streams = build.connection('streams')
    artifacts, resolve_artifacts = build.connection('artifacts')
    progress, resolve_progress = build.connection('progress')
    latest_progress, resolve_latest_progress = build.relationship('latest_progress')
    data, resolve_data = build.relationship('data')

    stream_status_summary = graphene.Field(lambda: JobExecutionStreamSummary)


class JobExecutionStreamSummary(graphene.ObjectType):
    queued = graphene.Int()
    active = graphene.Int()
    retry = graphene.Int()
    success = graphene.Int()
    failure = graphene.Int()

    @staticmethod
    def resolve_queued(instance, *_):
        return instance.get('QUEUED', 0)

    @staticmethod
    def resolve_active(instance, *_):
        return instance.get('ACTIVE', 0)

    @staticmethod
    def resolve_retry(instance, *_):
        return instance.get('RETRY', 0)

    @staticmethod
    def resolve_success(instance, *_):
        return instance.get('SUCCESS', 0)

    @staticmethod
    def resolve_failure(instance, *_):
        return instance.get('FAILURE', 0)


class ResourceData(ModelType):
    build = Builder(riberry.model.misc.ResourceData)

    name = build.field('name')
    value = build.field('name')


class JobExecutionArtifact(ModelType):
    build = Builder(riberry.model.job.JobExecutionArtifact)

    name = build.field('name')
    type, resolve_type = build.field('type'), simple_resolver('type')
    category = build.field('category')
    file_name = build.field('filename')
    created = build.field('created')
    size = build.field('size')

    content_type = graphene.String()
    content_encoding = graphene.String()

    data, resolve_data = build.relationship('data')


class JobExecutionArtifactData(ModelType):
    build = Builder(riberry.model.job.JobExecutionArtifactData)

    title = build.field('title')
    description = build.field('description')


class JobExecutionProgress(ModelType):
    build = Builder(riberry.model.job.JobExecutionProgress)

    created = build.field('created')
    message = build.field('message')


class JobExecutionStream(ModelType):
    build = Builder(riberry.model.job.JobExecutionStream)

    name = build.field('name')
    status = build.field('status')
    created = build.field('created')
    started = build.field('started')
    updated = build.field('updated')
    completed = build.field('completed')


class User(ModelType):
    build = Builder(riberry.model.auth.User)

    username = build.field('username')
    details, resolve_details = build.relationship('details')
    jobs, resolve_jobs = build.connection('jobs')
    executions, resolve_executions = build.connection('executions')
    groups = build.proxy(lambda: Group, is_list=True)
    forms = graphene.List(lambda: Form)
    applications = graphene.List(lambda: Application)


class UserDetails(ModelType):
    build = Builder(riberry.model.auth.UserDetails)

    display_name = build.field('display_name')
    first_name = build.field('first_name')
    last_name = build.field('last_name')
    department = build.field('department')
    email = build.field('email')
