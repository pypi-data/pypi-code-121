from tortoise import fields


class AuditMixin:
	created_at = fields.DatetimeField(null=True, auto_now_add=True)
	modified_at = fields.DatetimeField(null=True, auto_now=True)


class UuidMixin:
	uid = fields.UUIDField(pk=True)
