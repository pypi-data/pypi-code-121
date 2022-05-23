class InvalidBranchException(Exception):
	pass


class InvalidRemoteException(Exception):
	pass


class PatchError(Exception):
	pass


class CommandFailedError(Exception):
	pass


class PineNotFoundError(Exception):
	pass


class ValidationError(Exception):
	pass

class CannotUpdateReleasePine(ValidationError):
	pass

class FeatureDoesNotExistError(CommandFailedError):
	pass


class NotInPineDirectoryError(Exception):
	pass
