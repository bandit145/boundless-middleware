from marshmallow import Schema, fields


class MessageRequest(Schema):
    hash = fields.Str()
    search_keywords = fields.Dict()
    task = fields.Str()


class ReportRequest(Schema):
    id = fields.Str()
    service = fields.Str()
    incident_limit = fields.Int(default=10)
