import datetime

import pendulum
import riberry
from promise import Promise
from promise.dataloader import DataLoader
from sqlalchemy import DateTime


class PaginationDetails:

    def __init__(self, before, after, first, last, order_by):
        self.before = before
        self.after = after
        self.first = first
        self.last = last
        self.order_by = order_by

    def __hash__(self):
        return hash((
            self.before,
            self.after,
            self.first,
            self.last,
            self.order_by,
        ))

    def __eq__(self, other):
        return type(self) == type(other) and hash(self) == hash(other)


class PaginationLoader(DataLoader):

    def __init__(self, target_to_source_member, pagination_details, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_cls = target_to_source_member.model
        self.target_to_source_member = target_to_source_member
        self.details = pagination_details

    def batch_load_fn(self, models):
        return Promise.resolve([self.load_fn(model) for model in models])

    @staticmethod
    def cleanse_value(column, value):
        column_type = column.property.columns[0].type
        if isinstance(column_type, DateTime):
            dt: pendulum.DateTime = pendulum.parse(value)
            return datetime.datetime(
                year=dt.year,
                month=dt.month,
                day=dt.day,
                hour=dt.hour,
                minute=dt.minute,
                second=dt.second,
                microsecond=dt.microsecond,
                tzinfo=dt.timezone,
            )
        return value

    def load_fn(self, model):
        column = getattr(self.target_cls.model, self.details.order_by)

        query = riberry.model.conn.query(
            self.target_cls.model,
        ).join(
            self.target_to_source_member.member,
        ).filter(
            (type(model).id == model.id)
        )

        query_main = query
        if self.details.after is not None:
            query_main = query.filter(column > self.cleanse_value(column, self.details.after))
        if self.details.before is not None:
            query_main = query.filter(column < self.cleanse_value(column, self.details.before))

        if self.details.first is not None:
            query_main = query_main.order_by(column.asc()).limit(self.details.first)
        if self.details.last is not None:
            query_main = query_main.order_by(column.desc()).limit(self.details.last)

        result = query_main.all()
        filtered_result = riberry.policy.context.filter(result, action='view')
        filtered_result.sort(key=lambda x: getattr(x, self.details.order_by))

        min_value = getattr(filtered_result[0], self.details.order_by) if filtered_result else None
        max_value = getattr(filtered_result[-1], self.details.order_by) if filtered_result else None

        has_prev_page = bool(min_value is not None and query.filter(column < min_value).limit(1).first())
        has_next_page = bool(max_value is not None and query.filter(column > max_value).limit(1).first())

        return filtered_result, has_prev_page, has_next_page
