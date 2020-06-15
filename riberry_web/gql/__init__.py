import riberry
from autogqla.base import BaseModel

from . import model, query, schema

BaseModel.session_func = lambda: riberry.model.conn
