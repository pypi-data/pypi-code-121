from .errors import InvalidScopeError


validScope = [
	"account_admin",
	"global_admin",
	"media:create",
	"media:delete",
	"media:list",
	"media:modify",
	"media:upload",
	"playlist:create",
	"playlist:delete",
	"playlist:list",
	"playlist:modify",
]
"""List of valid scope values for the API"""
# FIXME maybe dict with explanation. Can dump on the commandline? or just in a doc.

scopeGroups = {
	"all": [
		"read",
		"write",
		"admin",
	],
	"admin": [
		"account_admin",
	],
	"read": [
		"media:list",
		"playlist:list",
	],
	"writeNoDelete": [
		"read",
		"media:create",
		"media:modify",
		"media:upload",
		"playlist:create",
		"playlist:modify",
	],
	"write": [
		"writeNoDelete",
		"media:delete",
		"playlist:delete",
	],
}
"""The scopes, grouped in some convenience groups"""


def resolve_scope(scope: set[str]) -> set[str]:
	resolved = set()
	for s in scope:
		if s in scopeGroups:
			resolved |= resolve_scope(set(scopeGroups[s]))
		elif s in validScope:
			resolved.add(s)
		else:
			raise InvalidScopeError(s)
	return resolved
