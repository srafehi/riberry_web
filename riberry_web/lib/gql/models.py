import graphene
import riberry

from .graphene_sqla.builder import Builder
from .graphene_sqla.helpers import non_null_list
from .graphene_sqla.wrapper_graphene import ModelType


class Application(ModelType):
    build = Builder(riberry.model.application.Application)

    # fields
    name = build.field('name')
    internal_name = build.field('internal_name')
    description = build.field('description')

    # relationships
    instances, resolve_instances = build.relationship('instances')
    forms, resolve_forms = build.relationship('forms')


class ApplicationInstance(ModelType):
    build = Builder(riberry.model.application.ApplicationInstance)

    # fields
    name = build.field('name')
    internal_name = build.field('internal_name')
    status = graphene.String()

    # relationships
    heartbeat, resolve_heartbeat = build.relationship('heartbeat')
    schedules, resolve_schedules = build.relationship('schedules')
    application, resolve_application = build.relationship('application')
    forms, resolve_forms = build.relationship('forms')


class ApplicationInstanceSchedule(ModelType):
    build = Builder(riberry.model.application.ApplicationInstanceSchedule)

    # fields
    days = build.field('days')
    start_time = build.field('start_time')
    end_time = build.field('end_time')
    timezone = build.field('timezone', name='timeZone')
    parameter = build.field('parameter')
    value = build.field('value')
    priority = build.field('priority')

    # relationships
    instance, resolve_instance = build.relationship('instance')


class Heartbeat(ModelType):
    build = Builder(riberry.model.application.Heartbeat)

    # fields
    created = build.field('created')
    updated = build.field('updated')

    # relationships
    instance, resolve_instance = build.relationship('instance')


class Form(ModelType):
    build = Builder(riberry.model.interface.Form)

    # fields
    name = build.field('name')
    internal_name = build.field('internal_name')
    description = build.field('description')
    version = build.field('version')

    # relationships
    instance, resolve_instance = build.relationship('instance')
    application, resolve_application = build.relationship('application')
    input_value_definitions, resolve_input_value_definitions = build.relationship('input_value_definitions')
    input_file_definitions, resolve_input_file_definitions = build.relationship('input_file_definitions')
    document, resolve_document = build.relationship('document')
    groups = build.proxy(lambda: Group, is_list=True)

    # connections
    jobs, resolve_jobs = build.connection('jobs', sortable_fields={
        'INTERNAL_ID': 'id',
        'NAME': 'name',
        'CREATED': 'created',
    })


class Document(ModelType):
    build = Builder(riberry.model.misc.Document)

    # fields
    type = build.field('type')
    content, resolve_content = build.field_with_resolver('content', lambda c: c.decode() if c else None)


class Group(ModelType):
    build = Builder(riberry.model.group.Group)

    # fields
    name = build.field('name')


class InputValueDefinition(ModelType):
    build = Builder(riberry.model.interface.InputValueDefinition)

    # fields
    name = build.field('name')
    internal_name = build.field('internal_name')
    description = build.field('description')
    type, resolve_type = build.field_with_resolver('type')
    required = build.field('required')
    default_value = graphene.JSONString()
    allowed_values = non_null_list(graphene.JSONString)


class InputFileDefinition(ModelType):
    build = Builder(riberry.model.interface.InputFileDefinition)

    # fields
    name = build.field('name')
    internal_name = build.field('internal_name')
    description = build.field('description')
    type, resolve_type = build.field_with_resolver('type')
    accept = build.field('accept')
    required = build.field('required')


class Job(ModelType):
    build = Builder(riberry.model.job.Job)

    # fields
    name = build.field('name')
    created = build.field('created')

    # relationships
    form, resolve_form = build.relationship('form')
    creator, resolve_creator = build.relationship('creator')

    # connections
    executions, resolve_executions = build.connection('executions', sortable_fields={
        'INTERNAL_ID': 'id',
        'CREATED': 'created',
        'UPDATED': 'updated',
    })


class JobExecution(ModelType):
    build = Builder(riberry.model.job.JobExecution)

    # fields
    status = build.field('status')
    created = build.field('created')
    started = build.field('started')
    updated = build.field('updated')
    completed = build.field('completed')
    task_id = build.field('task_id')
    priority = build.field('priority')
    stream_status_summary = graphene.Field(lambda: JobExecutionStreamSummary, required=True)

    # relationships
    creator, resolve_creator = build.relationship('creator')
    job, resolve_job = build.relationship('job')
    latest_progress, resolve_latest_progress = build.relationship('latest_progress', required=False)
    data, resolve_data = build.relationship('data')

    # connections
    streams, resolve_streams = build.connection('streams', sortable_fields={
        'INTERNAL_ID': 'id',
        'CREATED': 'created',
        'UPDATED': 'updated',
    })
    metrics, resolve_metrics = build.connection('metrics', sortable_fields={
        'INTERNAL_ID': 'id',
        'EPOCH_START': 'epoch_start',
        'EPOCH_END': 'epoch_end',
    })
    artifacts, resolve_artifacts = build.connection('artifacts')
    progress, resolve_progress = build.connection('progress')


class JobExecutionMetric(ModelType):
    build = Builder(riberry.model.job.JobExecutionMetric)

    # fields
    epoch_start = build.field('epoch_start')
    epoch_end = build.field('epoch_end')
    stream_name = build.field('stream_name')
    step_name = build.field('step_name')
    count = build.field('count')
    sum_duration = build.field('sum_duration')
    max_duration = build.field('max_duration')
    min_duration = build.field('min_duration')


class JobExecutionStreamSummary(graphene.ObjectType):
    # fields
    queued = graphene.Int(required=True)
    active = graphene.Int(required=True)
    retry = graphene.Int(required=True)
    success = graphene.Int(required=True)
    failure = graphene.Int(required=True)

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

    # fields
    name = build.field('name')
    value = build.field('name')


class JobExecutionArtifact(ModelType):
    build = Builder(riberry.model.job.JobExecutionArtifact)

    # fields
    name = build.field('name')
    type, resolve_type = build.field_with_resolver('type')
    category = build.field('category')
    filename = build.field('filename', name='fileName')
    created = build.field('created')
    size = build.field('size')
    content_type = graphene.String()
    content_encoding = graphene.String()

    # relationships
    data, resolve_data = build.relationship('data')


class JobExecutionArtifactData(ModelType):
    build = Builder(riberry.model.job.JobExecutionArtifactData)

    # fields
    title = build.field('title')
    description = build.field('description')


class JobExecutionProgress(ModelType):
    build = Builder(riberry.model.job.JobExecutionProgress)

    # fields
    created = build.field('created')
    message = build.field('message')


class JobExecutionStream(ModelType):
    build = Builder(riberry.model.job.JobExecutionStream)

    # fields
    name = build.field('name')
    status = build.field('status')
    created = build.field('created')
    started = build.field('started')
    updated = build.field('updated')
    completed = build.field('completed')

    # connections
    steps, resolve_steps = build.connection('steps', sortable_fields={
        'INTERNAL_ID': 'id',
        'CREATED': 'created',
        'UPDATED': 'updated',
    })


class JobExecutionStreamStep(ModelType):
    build = Builder(riberry.model.job.JobExecutionStreamStep)

    # fields
    name = build.field('name')
    status = build.field('status')
    created = build.field('created')
    started = build.field('started')
    updated = build.field('updated')
    completed = build.field('completed')


class User(ModelType):
    build = Builder(riberry.model.auth.User)

    # fields
    username = build.field('username')
    details, resolve_details = build.relationship('details')
    jobs, resolve_jobs = build.connection('jobs')

    # relationships
    groups = build.proxy(lambda: Group, is_list=True)
    forms = non_null_list(lambda: Form)
    applications = non_null_list(lambda: Application)

    # connections
    executions, resolve_executions = build.connection('executions')


class UserDetails(ModelType):
    build = Builder(riberry.model.auth.UserDetails)

    # fields
    display_name = build.field('display_name')
    first_name = build.field('first_name')
    last_name = build.field('last_name')
    department = build.field('department')
    email = build.field('email')
