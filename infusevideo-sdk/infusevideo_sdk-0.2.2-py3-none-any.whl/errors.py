class Error(Exception):
	pass


class AuthenticationError(Error):
	def __init__(self, errorType: str, errorMessage: str) -> None:
		self.errorType = errorType
		self.errorMessage = errorMessage
		super().__init__(f"{errorType}: {errorMessage}")


class AuthorizationError(Error):
	pass


class ScopeError(AuthorizationError):
	def __init__(self, scope: str, profile: "Profile", message: str) -> None:
		self.scope = scope
		self.profile = profile
		self.message = message
		super().__init__(message)

	def __str__(self) -> str:
		return self.message


class UnrequestedScopeError(ScopeError):
	def __init__(self, scope: str, profile: "Profile") -> None:
		message = (
			f"The scope '{scope}' is required for this action, but it has not been enabled in "
			f"the configuration for this profile ({profile.name}). Please add it and try again."
		)
		super().__init__(scope, profile, message)


class RequestedScopeError(ScopeError):
	def __init__(self, scope: str, profile: "Profile") -> None:
		message = (
			f"The scope '{scope}' is required for this action, and it has been correctly enabled "
			f"in the configuration for this profile ({profile.name}). However, it was not granted "
			"to your token. You most likely do not have access to this scope. If you have been "
			"granted this permission by an administrator since, refresh your token."
		)
		super().__init__(scope, profile, message)


class ConfigurationError(Error):
	pass


class ConfigAlreadyExists(Error):
	def __init__(self, filename: str) -> None:
		self.filename = filename
		super().__init__(
			f"The configuration file already exists at {filename}. Not doing anything.",
		)


class ConfigNotFound(Error):
	def __init__(self, filename: str, message: str = "") -> None:
		self.filename = filename
		self.message = message
		super().__init__(
			f"No configuration file found, exiting. Please create one at {filename}. {message}",
		)


class InvalidScopeError(Error):
	def __init__(self, scope: str) -> None:
		self.scope = scope
		super().__init__(f"Invalid scope: '{scope}'")


class ListenerBindError(Error):
	pass


class ApiError(Error):
	def __init__(self, response: "Response"):
		self.response = response
		super().__init__(response)


class ApiResponseDecodeError(Error):
	pass
