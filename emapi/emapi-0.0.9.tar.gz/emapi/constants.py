from dataclasses import _MISSING_TYPE

OPENAPI_FIELDS = {
	"int": ("integer", "int64"),
	"UUIDField": ("string", "uuid"),
	"DatetimeField": ("string", "date-time"),
	"CharField": ("string",),
	"BooleanField": ("boolean",),
	_MISSING_TYPE: ("",),
	str: ("string",),
}
