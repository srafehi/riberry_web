from __future__ import annotations

import graphene
import riberry
from autogqla import create
from autogqla.base import BaseModel
from autogqla.spec import ModelSpec, RelationshipsSpec, RelationshipSpec, FieldsSpec


class ApplicationInstance(BaseModel):
    __spec__ = ModelSpec(
        model=riberry.model.application.ApplicationInstance,
    )
    status = graphene.String()


class JobExecution(BaseModel):
    __spec__ = ModelSpec(
        model=riberry.model.job.JobExecution,
        relationships=RelationshipsSpec(
            specs={
                'latest_progress': RelationshipSpec(props={
                    'required': False,
                }),
            }
        )
    )


class User(BaseModel):
    __spec__ = ModelSpec(
        model=riberry.model.auth.User,
        fields=FieldsSpec(
            exclude=['password']
        )
    )


create(riberry.model.base.Base)
