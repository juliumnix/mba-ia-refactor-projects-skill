from marshmallow import Schema, fields, EXCLUDE


class TaskSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    title = fields.Str()
    description = fields.Str(load_default="")
    status = fields.Str()
    priority = fields.Int()
    user_id = fields.Int(allow_none=True)
    category_id = fields.Int(allow_none=True)
    due_date = fields.Str(allow_none=True)
    tags = fields.Raw(allow_none=True)


class TaskCreateSchema(TaskSchema):
    pass


class UserCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str()
    email = fields.Str()
    password = fields.Str()
    role = fields.Str(load_default="user")
