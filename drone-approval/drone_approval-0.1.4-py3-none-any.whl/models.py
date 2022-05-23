from tortoise.models import Model
from tortoise import fields

class ApprovalRequest(Model):
    id = fields.UUIDField(pk=True)
    name = fields.TextField()
    repo = fields.TextField()
    build = fields.IntField()
    stage = fields.IntField()
    step = fields.IntField()
    approval_timestamp = fields.data.DatetimeField(null=True)
    created_at = fields.data.DatetimeField(null=False)
    created_by = fields.TextField()
    groups: fields.ReverseRelation['ApprovalGroup']
    approved_build: fields.ReverseRelation['ApprovedBuild']
    declined_timestamp = fields.data.DatetimeField(null=True)

    def __str__(self):
        return f'{self.repo}/{self.build}/{self.stage}/{self.step}'

class ApprovalGroup(Model):
    id = fields.UUIDField(pk=True)
    name = fields.TextField()
    count = fields.IntField()
    request: fields.ForeignKeyRelation[ApprovalRequest] = fields.ForeignKeyField(
        'models.ApprovalRequest', related_name='groups',
    )
    approval_timestamp = fields.data.DatetimeField(null=True)
    users: fields.ReverseRelation['Approval']

class Approval(Model):
    id = fields.UUIDField(pk=True)
    group: fields.ForeignKeyRelation[ApprovalGroup] = fields.ForeignKeyField(
        'models.ApprovalGroup', related_name='users',
    )
    user_email = fields.TextField()
    secret = fields.TextField(null=True)
    approval_timestamp = fields.data.DatetimeField(null=True)
    declined_timestamp = fields.data.DatetimeField(null=True)

class ApprovalResult(Model):
    id = fields.UUIDField(pk=True)
    request: fields.ForeignKeyRelation[ApprovalRequest] = fields.ForeignKeyField(
        'models.ApprovalRequest', related_name='approved_build',
    )
    build = fields.IntField(null=False)
    repo = fields.TextField(null=False)
    created_at = fields.DatetimeField(null=True)
    approved = fields.BooleanField(default=False)
