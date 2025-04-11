from marshmallow import fields, Schema

class AdminSchema(Schema):
    id = fields.String()
    username = fields.String()
    quizzes = fields.String()