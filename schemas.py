from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    # Поле може бути порожнім (для загальних категорій)
    user_id = fields.Int(allow_none=True)

class RecordSchema(Schema):
    id = fields.Int(dump_only=True)
    sum = fields.Float(required=True)
    user_id = fields.Int(required=True)
    category_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)