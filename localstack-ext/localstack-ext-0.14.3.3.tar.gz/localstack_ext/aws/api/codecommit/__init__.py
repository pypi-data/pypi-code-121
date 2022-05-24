import sys
from datetime import datetime
from typing import Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

AccountId = str
AdditionalData = str
ApprovalRuleContent = str
ApprovalRuleId = str
ApprovalRuleName = str
ApprovalRuleTemplateContent = str
ApprovalRuleTemplateDescription = str
ApprovalRuleTemplateId = str
ApprovalRuleTemplateName = str
Approved = bool
Arn = str
BranchName = str
CapitalBoolean = bool
ClientRequestToken = str
CloneUrlHttp = str
CloneUrlSsh = str
CommentId = str
CommitId = str
CommitName = str
Content = str
Count = int
Date = str
Description = str
Email = str
ErrorCode = str
ErrorMessage = str
ExceptionName = str
HunkContent = str
IsCommentDeleted = bool
IsContentConflict = bool
IsFileModeConflict = bool
IsHunkConflict = bool
IsMergeable = bool
IsMerged = bool
IsMove = bool
IsObjectTypeConflict = bool
KeepEmptyFolders = bool
Limit = int
LineNumber = int
MaxResults = int
Message = str
Mode = str
Name = str
NextToken = str
NumberOfConflicts = int
ObjectId = str
Overridden = bool
Path = str
PullRequestId = str
ReactionEmoji = str
ReactionShortCode = str
ReactionUnicode = str
ReactionValue = str
ReferenceName = str
RepositoryDescription = str
RepositoryId = str
RepositoryName = str
RepositoryTriggerCustomData = str
RepositoryTriggerExecutionFailureMessage = str
RepositoryTriggerName = str
RepositoryTriggersConfigurationId = str
ResourceArn = str
RevisionId = str
RuleContentSha256 = str
TagKey = str
TagValue = str
Title = str


class ApprovalState(str):
    APPROVE = "APPROVE"
    REVOKE = "REVOKE"


class ChangeTypeEnum(str):
    A = "A"
    M = "M"
    D = "D"


class ConflictDetailLevelTypeEnum(str):
    FILE_LEVEL = "FILE_LEVEL"
    LINE_LEVEL = "LINE_LEVEL"


class ConflictResolutionStrategyTypeEnum(str):
    NONE = "NONE"
    ACCEPT_SOURCE = "ACCEPT_SOURCE"
    ACCEPT_DESTINATION = "ACCEPT_DESTINATION"
    AUTOMERGE = "AUTOMERGE"


class FileModeTypeEnum(str):
    EXECUTABLE = "EXECUTABLE"
    NORMAL = "NORMAL"
    SYMLINK = "SYMLINK"


class MergeOptionTypeEnum(str):
    FAST_FORWARD_MERGE = "FAST_FORWARD_MERGE"
    SQUASH_MERGE = "SQUASH_MERGE"
    THREE_WAY_MERGE = "THREE_WAY_MERGE"


class ObjectTypeEnum(str):
    FILE = "FILE"
    DIRECTORY = "DIRECTORY"
    GIT_LINK = "GIT_LINK"
    SYMBOLIC_LINK = "SYMBOLIC_LINK"


class OrderEnum(str):
    ascending = "ascending"
    descending = "descending"


class OverrideStatus(str):
    OVERRIDE = "OVERRIDE"
    REVOKE = "REVOKE"


class PullRequestEventType(str):
    PULL_REQUEST_CREATED = "PULL_REQUEST_CREATED"
    PULL_REQUEST_STATUS_CHANGED = "PULL_REQUEST_STATUS_CHANGED"
    PULL_REQUEST_SOURCE_REFERENCE_UPDATED = "PULL_REQUEST_SOURCE_REFERENCE_UPDATED"
    PULL_REQUEST_MERGE_STATE_CHANGED = "PULL_REQUEST_MERGE_STATE_CHANGED"
    PULL_REQUEST_APPROVAL_RULE_CREATED = "PULL_REQUEST_APPROVAL_RULE_CREATED"
    PULL_REQUEST_APPROVAL_RULE_UPDATED = "PULL_REQUEST_APPROVAL_RULE_UPDATED"
    PULL_REQUEST_APPROVAL_RULE_DELETED = "PULL_REQUEST_APPROVAL_RULE_DELETED"
    PULL_REQUEST_APPROVAL_RULE_OVERRIDDEN = "PULL_REQUEST_APPROVAL_RULE_OVERRIDDEN"
    PULL_REQUEST_APPROVAL_STATE_CHANGED = "PULL_REQUEST_APPROVAL_STATE_CHANGED"


class PullRequestStatusEnum(str):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class RelativeFileVersionEnum(str):
    BEFORE = "BEFORE"
    AFTER = "AFTER"


class ReplacementTypeEnum(str):
    KEEP_BASE = "KEEP_BASE"
    KEEP_SOURCE = "KEEP_SOURCE"
    KEEP_DESTINATION = "KEEP_DESTINATION"
    USE_NEW_CONTENT = "USE_NEW_CONTENT"


class RepositoryTriggerEventEnum(str):
    all = "all"
    updateReference = "updateReference"
    createReference = "createReference"
    deleteReference = "deleteReference"


class SortByEnum(str):
    repositoryName = "repositoryName"
    lastModifiedDate = "lastModifiedDate"


class ActorDoesNotExistException(ServiceException):
    """The specified Amazon Resource Name (ARN) does not exist in the AWS
    account.
    """


class ApprovalRuleContentRequiredException(ServiceException):
    """The content for the approval rule is empty. You must provide some
    content for an approval rule. The content cannot be null.
    """


class ApprovalRuleDoesNotExistException(ServiceException):
    """The specified approval rule does not exist."""


class ApprovalRuleNameAlreadyExistsException(ServiceException):
    """An approval rule with that name already exists. Approval rule names must
    be unique within the scope of a pull request.
    """


class ApprovalRuleNameRequiredException(ServiceException):
    """An approval rule name is required, but was not specified."""


class ApprovalRuleTemplateContentRequiredException(ServiceException):
    """The content for the approval rule template is empty. You must provide
    some content for an approval rule template. The content cannot be null.
    """


class ApprovalRuleTemplateDoesNotExistException(ServiceException):
    """The specified approval rule template does not exist. Verify that the
    name is correct and that you are signed in to the AWS Region where the
    template was created, and then try again.
    """


class ApprovalRuleTemplateInUseException(ServiceException):
    """The approval rule template is associated with one or more repositories.
    You cannot delete a template that is associated with a repository.
    Remove all associations, and then try again.
    """


class ApprovalRuleTemplateNameAlreadyExistsException(ServiceException):
    """You cannot create an approval rule template with that name because a
    template with that name already exists in this AWS Region for your AWS
    account. Approval rule template names must be unique.
    """


class ApprovalRuleTemplateNameRequiredException(ServiceException):
    """An approval rule template name is required, but was not specified."""


class ApprovalStateRequiredException(ServiceException):
    """An approval state is required, but was not specified."""


class AuthorDoesNotExistException(ServiceException):
    """The specified Amazon Resource Name (ARN) does not exist in the AWS
    account.
    """


class BeforeCommitIdAndAfterCommitIdAreSameException(ServiceException):
    """The before commit ID and the after commit ID are the same, which is not
    valid. The before commit ID and the after commit ID must be different
    commit IDs.
    """


class BlobIdDoesNotExistException(ServiceException):
    """The specified blob does not exist."""


class BlobIdRequiredException(ServiceException):
    """A blob ID is required, but was not specified."""


class BranchDoesNotExistException(ServiceException):
    """The specified branch does not exist."""


class BranchNameExistsException(ServiceException):
    """Cannot create the branch with the specified name because the commit
    conflicts with an existing branch with the same name. Branch names must
    be unique.
    """


class BranchNameIsTagNameException(ServiceException):
    """The specified branch name is not valid because it is a tag name. Enter
    the name of a branch in the repository. For a list of valid branch
    names, use ListBranches.
    """


class BranchNameRequiredException(ServiceException):
    """A branch name is required, but was not specified."""


class CannotDeleteApprovalRuleFromTemplateException(ServiceException):
    """The approval rule cannot be deleted from the pull request because it was
    created by an approval rule template and applied to the pull request
    automatically.
    """


class CannotModifyApprovalRuleFromTemplateException(ServiceException):
    """The approval rule cannot be modified for the pull request because it was
    created by an approval rule template and applied to the pull request
    automatically.
    """


class ClientRequestTokenRequiredException(ServiceException):
    """A client request token is required. A client request token is an unique,
    client-generated idempotency token that, when provided in a request,
    ensures the request cannot be repeated with a changed parameter. If a
    request is received with the same parameters and a token is included,
    the request returns information about the initial request that used that
    token.
    """


class CommentContentRequiredException(ServiceException):
    """The comment is empty. You must provide some content for a comment. The
    content cannot be null.
    """


class CommentContentSizeLimitExceededException(ServiceException):
    """The comment is too large. Comments are limited to 1,000 characters."""


class CommentDeletedException(ServiceException):
    """This comment has already been deleted. You cannot edit or delete a
    deleted comment.
    """


class CommentDoesNotExistException(ServiceException):
    """No comment exists with the provided ID. Verify that you have used the
    correct ID, and then try again.
    """


class CommentIdRequiredException(ServiceException):
    """The comment ID is missing or null. A comment ID is required."""


class CommentNotCreatedByCallerException(ServiceException):
    """You cannot modify or delete this comment. Only comment authors can
    modify or delete their comments.
    """


class CommitDoesNotExistException(ServiceException):
    """The specified commit does not exist or no commit was specified, and the
    specified repository has no default branch.
    """


class CommitIdDoesNotExistException(ServiceException):
    """The specified commit ID does not exist."""


class CommitIdRequiredException(ServiceException):
    """A commit ID was not specified."""


class CommitIdsLimitExceededException(ServiceException):
    """The maximum number of allowed commit IDs in a batch request is 100.
    Verify that your batch requests contains no more than 100 commit IDs,
    and then try again.
    """


class CommitIdsListRequiredException(ServiceException):
    """A list of commit IDs is required, but was either not specified or the
    list was empty.
    """


class CommitMessageLengthExceededException(ServiceException):
    """The commit message is too long. Provide a shorter string."""


class CommitRequiredException(ServiceException):
    """A commit was not specified."""


class ConcurrentReferenceUpdateException(ServiceException):
    """The merge cannot be completed because the target branch has been
    modified. Another user might have modified the target branch while the
    merge was in progress. Wait a few minutes, and then try again.
    """


class DefaultBranchCannotBeDeletedException(ServiceException):
    """The specified branch is the default branch for the repository, and
    cannot be deleted. To delete this branch, you must first set another
    branch as the default branch.
    """


class DirectoryNameConflictsWithFileNameException(ServiceException):
    """A file cannot be added to the repository because the specified path name
    has the same name as a file that already exists in this repository.
    Either provide a different name for the file, or specify a different
    path for the file.
    """


class EncryptionIntegrityChecksFailedException(ServiceException):
    """An encryption integrity check failed."""


class EncryptionKeyAccessDeniedException(ServiceException):
    """An encryption key could not be accessed."""


class EncryptionKeyDisabledException(ServiceException):
    """The encryption key is disabled."""


class EncryptionKeyNotFoundException(ServiceException):
    """No encryption key was found."""


class EncryptionKeyUnavailableException(ServiceException):
    """The encryption key is not available."""


class FileContentAndSourceFileSpecifiedException(ServiceException):
    """The commit cannot be created because both a source file and file content
    have been specified for the same file. You cannot provide both. Either
    specify a source file or provide the file content directly.
    """


class FileContentRequiredException(ServiceException):
    """The file cannot be added because it is empty. Empty files cannot be
    added to the repository with this API.
    """


class FileContentSizeLimitExceededException(ServiceException):
    """The file cannot be added because it is too large. The maximum file size
    is 6 MB, and the combined file content change size is 7 MB. Consider
    making these changes using a Git client.
    """


class FileDoesNotExistException(ServiceException):
    """The specified file does not exist. Verify that you have used the correct
    file name, full path, and extension.
    """


class FileEntryRequiredException(ServiceException):
    """The commit cannot be created because no files have been specified as
    added, updated, or changed (PutFile or DeleteFile) for the commit.
    """


class FileModeRequiredException(ServiceException):
    """The commit cannot be created because no file mode has been specified. A
    file mode is required to update mode permissions for a file.
    """


class FileNameConflictsWithDirectoryNameException(ServiceException):
    """A file cannot be added to the repository because the specified file name
    has the same name as a directory in this repository. Either provide
    another name for the file, or add the file in a directory that does not
    match the file name.
    """


class FilePathConflictsWithSubmodulePathException(ServiceException):
    """The commit cannot be created because a specified file path points to a
    submodule. Verify that the destination files have valid file paths that
    do not point to a submodule.
    """


class FileTooLargeException(ServiceException):
    """The specified file exceeds the file size limit for AWS CodeCommit. For
    more information about limits in AWS CodeCommit, see `AWS CodeCommit
    User
    Guide <https://docs.aws.amazon.com/codecommit/latest/userguide/limits.html>`__.
    """


class FolderContentSizeLimitExceededException(ServiceException):
    """The commit cannot be created because at least one of the overall changes
    in the commit results in a folder whose contents exceed the limit of 6
    MB. Either reduce the number and size of your changes, or split the
    changes across multiple folders.
    """


class FolderDoesNotExistException(ServiceException):
    """The specified folder does not exist. Either the folder name is not
    correct, or you did not enter the full path to the folder.
    """


class IdempotencyParameterMismatchException(ServiceException):
    """The client request token is not valid. Either the token is not in a
    valid format, or the token has been used in a previous request and
    cannot be reused.
    """


class InvalidActorArnException(ServiceException):
    """The Amazon Resource Name (ARN) is not valid. Make sure that you have
    provided the full ARN for the user who initiated the change for the pull
    request, and then try again.
    """


class InvalidApprovalRuleContentException(ServiceException):
    """The content for the approval rule is not valid."""


class InvalidApprovalRuleNameException(ServiceException):
    """The name for the approval rule is not valid."""


class InvalidApprovalRuleTemplateContentException(ServiceException):
    """The content of the approval rule template is not valid."""


class InvalidApprovalRuleTemplateDescriptionException(ServiceException):
    """The description for the approval rule template is not valid because it
    exceeds the maximum characters allowed for a description. For more
    information about limits in AWS CodeCommit, see `AWS CodeCommit User
    Guide <https://docs.aws.amazon.com/codecommit/latest/userguide/limits.html>`__.
    """


class InvalidApprovalRuleTemplateNameException(ServiceException):
    """The name of the approval rule template is not valid. Template names must
    be between 1 and 100 valid characters in length. For more information
    about limits in AWS CodeCommit, see `AWS CodeCommit User
    Guide <https://docs.aws.amazon.com/codecommit/latest/userguide/limits.html>`__.
    """


class InvalidApprovalStateException(ServiceException):
    """The state for the approval is not valid. Valid values include APPROVE
    and REVOKE.
    """


class InvalidAuthorArnException(ServiceException):
    """The Amazon Resource Name (ARN) is not valid. Make sure that you have
    provided the full ARN for the author of the pull request, and then try
    again.
    """


class InvalidBlobIdException(ServiceException):
    """The specified blob is not valid."""


class InvalidBranchNameException(ServiceException):
    """The specified reference name is not valid."""


class InvalidClientRequestTokenException(ServiceException):
    """The client request token is not valid."""


class InvalidCommentIdException(ServiceException):
    """The comment ID is not in a valid format. Make sure that you have
    provided the full comment ID.
    """


class InvalidCommitException(ServiceException):
    """The specified commit is not valid."""


class InvalidCommitIdException(ServiceException):
    """The specified commit ID is not valid."""


class InvalidConflictDetailLevelException(ServiceException):
    """The specified conflict detail level is not valid."""


class InvalidConflictResolutionException(ServiceException):
    """The specified conflict resolution list is not valid."""


class InvalidConflictResolutionStrategyException(ServiceException):
    """The specified conflict resolution strategy is not valid."""


class InvalidContinuationTokenException(ServiceException):
    """The specified continuation token is not valid."""


class InvalidDeletionParameterException(ServiceException):
    """The specified deletion parameter is not valid."""


class InvalidDescriptionException(ServiceException):
    """The pull request description is not valid. Descriptions cannot be more
    than 1,000 characters.
    """


class InvalidDestinationCommitSpecifierException(ServiceException):
    """The destination commit specifier is not valid. You must provide a valid
    branch name, tag, or full commit ID.
    """


class InvalidEmailException(ServiceException):
    """The specified email address either contains one or more characters that
    are not allowed, or it exceeds the maximum number of characters allowed
    for an email address.
    """


class InvalidFileLocationException(ServiceException):
    """The location of the file is not valid. Make sure that you include the
    file name and extension.
    """


class InvalidFileModeException(ServiceException):
    """The specified file mode permission is not valid. For a list of valid
    file mode permissions, see PutFile.
    """


class InvalidFilePositionException(ServiceException):
    """The position is not valid. Make sure that the line number exists in the
    version of the file you want to comment on.
    """


class InvalidMaxConflictFilesException(ServiceException):
    """The specified value for the number of conflict files to return is not
    valid.
    """


class InvalidMaxMergeHunksException(ServiceException):
    """The specified value for the number of merge hunks to return is not
    valid.
    """


class InvalidMaxResultsException(ServiceException):
    """The specified number of maximum results is not valid."""


class InvalidMergeOptionException(ServiceException):
    """The specified merge option is not valid for this operation. Not all
    merge strategies are supported for all operations.
    """


class InvalidOrderException(ServiceException):
    """The specified sort order is not valid."""


class InvalidOverrideStatusException(ServiceException):
    """The override status is not valid. Valid statuses are OVERRIDE and
    REVOKE.
    """


class InvalidParentCommitIdException(ServiceException):
    """The parent commit ID is not valid. The commit ID cannot be empty, and
    must match the head commit ID for the branch of the repository where you
    want to add or update a file.
    """


class InvalidPathException(ServiceException):
    """The specified path is not valid."""


class InvalidPullRequestEventTypeException(ServiceException):
    """The pull request event type is not valid."""


class InvalidPullRequestIdException(ServiceException):
    """The pull request ID is not valid. Make sure that you have provided the
    full ID and that the pull request is in the specified repository, and
    then try again.
    """


class InvalidPullRequestStatusException(ServiceException):
    """The pull request status is not valid. The only valid values are ``OPEN``
    and ``CLOSED``.
    """


class InvalidPullRequestStatusUpdateException(ServiceException):
    """The pull request status update is not valid. The only valid update is
    from ``OPEN`` to ``CLOSED``.
    """


class InvalidReactionUserArnException(ServiceException):
    """The Amazon Resource Name (ARN) of the user or identity is not valid."""


class InvalidReactionValueException(ServiceException):
    """The value of the reaction is not valid. For more information, see the
    `AWS CodeCommit User
    Guide <https://docs.aws.amazon.com/codecommit/latest/userguide/welcome.html>`__.
    """


class InvalidReferenceNameException(ServiceException):
    """The specified reference name format is not valid. Reference names must
    conform to the Git references format (for example, refs/heads/master).
    For more information, see `Git Internals - Git
    References <https://git-scm.com/book/en/v2/Git-Internals-Git-References>`__
    or consult your Git documentation.
    """


class InvalidRelativeFileVersionEnumException(ServiceException):
    """Either the enum is not in a valid format, or the specified file version
    enum is not valid in respect to the current file version.
    """


class InvalidReplacementContentException(ServiceException):
    """Automerge was specified for resolving the conflict, but the replacement
    type is not valid or content is missing.
    """


class InvalidReplacementTypeException(ServiceException):
    """Automerge was specified for resolving the conflict, but the specified
    replacement type is not valid.
    """


class InvalidRepositoryDescriptionException(ServiceException):
    """The specified repository description is not valid."""


class InvalidRepositoryNameException(ServiceException):
    """A specified repository name is not valid.

    This exception occurs only when a specified repository name is not
    valid. Other exceptions occur when a required repository parameter is
    missing, or when a specified repository does not exist.
    """


class InvalidRepositoryTriggerBranchNameException(ServiceException):
    """One or more branch names specified for the trigger is not valid."""


class InvalidRepositoryTriggerCustomDataException(ServiceException):
    """The custom data provided for the trigger is not valid."""


class InvalidRepositoryTriggerDestinationArnException(ServiceException):
    """The Amazon Resource Name (ARN) for the trigger is not valid for the
    specified destination. The most common reason for this error is that the
    ARN does not meet the requirements for the service type.
    """


class InvalidRepositoryTriggerEventsException(ServiceException):
    """One or more events specified for the trigger is not valid. Check to make
    sure that all events specified match the requirements for allowed
    events.
    """


class InvalidRepositoryTriggerNameException(ServiceException):
    """The name of the trigger is not valid."""


class InvalidRepositoryTriggerRegionException(ServiceException):
    """The AWS Region for the trigger target does not match the AWS Region for
    the repository. Triggers must be created in the same Region as the
    target for the trigger.
    """


class InvalidResourceArnException(ServiceException):
    """The value for the resource ARN is not valid. For more information about
    resources in AWS CodeCommit, see `CodeCommit Resources and
    Operations <https://docs.aws.amazon.com/codecommit/latest/userguide/auth-and-access-control-iam-access-control-identity-based.html#arn-formats>`__
    in the AWS CodeCommit User Guide.
    """


class InvalidRevisionIdException(ServiceException):
    """The revision ID is not valid. Use GetPullRequest to determine the value."""


class InvalidRuleContentSha256Exception(ServiceException):
    """The SHA-256 hash signature for the rule content is not valid."""


class InvalidSortByException(ServiceException):
    """The specified sort by value is not valid."""


class InvalidSourceCommitSpecifierException(ServiceException):
    """The source commit specifier is not valid. You must provide a valid
    branch name, tag, or full commit ID.
    """


class InvalidSystemTagUsageException(ServiceException):
    """The specified tag is not valid. Key names cannot be prefixed with aws:."""


class InvalidTagKeysListException(ServiceException):
    """The list of tags is not valid."""


class InvalidTagsMapException(ServiceException):
    """The map of tags is not valid."""


class InvalidTargetBranchException(ServiceException):
    """The specified target branch is not valid."""


class InvalidTargetException(ServiceException):
    """The target for the pull request is not valid. A target must contain the
    full values for the repository name, source branch, and destination
    branch for the pull request.
    """


class InvalidTargetsException(ServiceException):
    """The targets for the pull request is not valid or not in a valid format.
    Targets are a list of target objects. Each target object must contain
    the full values for the repository name, source branch, and destination
    branch for a pull request.
    """


class InvalidTitleException(ServiceException):
    """The title of the pull request is not valid. Pull request titles cannot
    exceed 100 characters in length.
    """


class ManualMergeRequiredException(ServiceException):
    """The pull request cannot be merged automatically into the destination
    branch. You must manually merge the branches and resolve any conflicts.
    """


class MaximumBranchesExceededException(ServiceException):
    """The number of branches for the trigger was exceeded."""


class MaximumConflictResolutionEntriesExceededException(ServiceException):
    """The number of allowed conflict resolution entries was exceeded."""


class MaximumFileContentToLoadExceededException(ServiceException):
    """The number of files to load exceeds the allowed limit."""


class MaximumFileEntriesExceededException(ServiceException):
    """The number of specified files to change as part of this commit exceeds
    the maximum number of files that can be changed in a single commit.
    Consider using a Git client for these changes.
    """


class MaximumItemsToCompareExceededException(ServiceException):
    """The number of items to compare between the source or destination
    branches and the merge base has exceeded the maximum allowed.
    """


class MaximumNumberOfApprovalsExceededException(ServiceException):
    """The number of approvals required for the approval rule exceeds the
    maximum number allowed.
    """


class MaximumOpenPullRequestsExceededException(ServiceException):
    """You cannot create the pull request because the repository has too many
    open pull requests. The maximum number of open pull requests for a
    repository is 1,000. Close one or more open pull requests, and then try
    again.
    """


class MaximumRepositoryNamesExceededException(ServiceException):
    """The maximum number of allowed repository names was exceeded. Currently,
    this number is 100.
    """


class MaximumRepositoryTriggersExceededException(ServiceException):
    """The number of triggers allowed for the repository was exceeded."""


class MaximumRuleTemplatesAssociatedWithRepositoryException(ServiceException):
    """The maximum number of approval rule templates for a repository has been
    exceeded. You cannot associate more than 25 approval rule templates with
    a repository.
    """


class MergeOptionRequiredException(ServiceException):
    """A merge option or stategy is required, and none was provided."""


class MultipleConflictResolutionEntriesException(ServiceException):
    """More than one conflict resolution entries exists for the conflict. A
    conflict can have only one conflict resolution entry.
    """


class MultipleRepositoriesInPullRequestException(ServiceException):
    """You cannot include more than one repository in a pull request. Make sure
    you have specified only one repository name in your request, and then
    try again.
    """


class NameLengthExceededException(ServiceException):
    """The user name is not valid because it has exceeded the character limit
    for author names.
    """


class NoChangeException(ServiceException):
    """The commit cannot be created because no changes will be made to the
    repository as a result of this commit. A commit must contain at least
    one change.
    """


class NumberOfRuleTemplatesExceededException(ServiceException):
    """The maximum number of approval rule templates has been exceeded for this
    AWS Region.
    """


class NumberOfRulesExceededException(ServiceException):
    """The approval rule cannot be added. The pull request has the maximum
    number of approval rules associated with it.
    """


class OverrideAlreadySetException(ServiceException):
    """The pull request has already had its approval rules set to override."""


class OverrideStatusRequiredException(ServiceException):
    """An override status is required, but no value was provided. Valid values
    include OVERRIDE and REVOKE.
    """


class ParentCommitDoesNotExistException(ServiceException):
    """The parent commit ID is not valid because it does not exist. The
    specified parent commit ID does not exist in the specified branch of the
    repository.
    """


class ParentCommitIdOutdatedException(ServiceException):
    """The file could not be added because the provided parent commit ID is not
    the current tip of the specified branch. To view the full commit ID of
    the current head of the branch, use GetBranch.
    """


class ParentCommitIdRequiredException(ServiceException):
    """A parent commit ID is required. To view the full commit ID of a branch
    in a repository, use GetBranch or a Git command (for example, git pull
    or git log).
    """


class PathDoesNotExistException(ServiceException):
    """The specified path does not exist."""


class PathRequiredException(ServiceException):
    """The folderPath for a location cannot be null."""


class PullRequestAlreadyClosedException(ServiceException):
    """The pull request status cannot be updated because it is already closed."""


class PullRequestApprovalRulesNotSatisfiedException(ServiceException):
    """The pull request cannot be merged because one or more approval rules
    applied to the pull request have conditions that have not been met.
    """


class PullRequestCannotBeApprovedByAuthorException(ServiceException):
    """The approval cannot be applied because the user approving the pull
    request matches the user who created the pull request. You cannot
    approve a pull request that you created.
    """


class PullRequestDoesNotExistException(ServiceException):
    """The pull request ID could not be found. Make sure that you have
    specified the correct repository name and pull request ID, and then try
    again.
    """


class PullRequestIdRequiredException(ServiceException):
    """A pull request ID is required, but none was provided."""


class PullRequestStatusRequiredException(ServiceException):
    """A pull request status is required, but none was provided."""


class PutFileEntryConflictException(ServiceException):
    """The commit cannot be created because one or more files specified in the
    commit reference both a file and a folder.
    """


class ReactionLimitExceededException(ServiceException):
    """The number of reactions has been exceeded. Reactions are limited to one
    reaction per user for each individual comment ID.
    """


class ReactionValueRequiredException(ServiceException):
    """A reaction value is required."""


class ReferenceDoesNotExistException(ServiceException):
    """The specified reference does not exist. You must provide a full commit
    ID.
    """


class ReferenceNameRequiredException(ServiceException):
    """A reference name is required, but none was provided."""


class ReferenceTypeNotSupportedException(ServiceException):
    """The specified reference is not a supported type."""


class ReplacementContentRequiredException(ServiceException):
    """USE_NEW_CONTENT was specified, but no replacement content has been
    provided.
    """


class ReplacementTypeRequiredException(ServiceException):
    """A replacement type is required."""


class RepositoryDoesNotExistException(ServiceException):
    """The specified repository does not exist."""


class RepositoryLimitExceededException(ServiceException):
    """A repository resource limit was exceeded."""


class RepositoryNameExistsException(ServiceException):
    """The specified repository name already exists."""


class RepositoryNameRequiredException(ServiceException):
    """A repository name is required, but was not specified."""


class RepositoryNamesRequiredException(ServiceException):
    """At least one repository name object is required, but was not specified."""


class RepositoryNotAssociatedWithPullRequestException(ServiceException):
    """The repository does not contain any pull requests with that pull request
    ID. Use GetPullRequest to verify the correct repository name for the
    pull request ID.
    """


class RepositoryTriggerBranchNameListRequiredException(ServiceException):
    """At least one branch name is required, but was not specified in the
    trigger configuration.
    """


class RepositoryTriggerDestinationArnRequiredException(ServiceException):
    """A destination ARN for the target service for the trigger is required,
    but was not specified.
    """


class RepositoryTriggerEventsListRequiredException(ServiceException):
    """At least one event for the trigger is required, but was not specified."""


class RepositoryTriggerNameRequiredException(ServiceException):
    """A name for the trigger is required, but was not specified."""


class RepositoryTriggersListRequiredException(ServiceException):
    """The list of triggers for the repository is required, but was not
    specified.
    """


class ResourceArnRequiredException(ServiceException):
    """A valid Amazon Resource Name (ARN) for an AWS CodeCommit resource is
    required. For a list of valid resources in AWS CodeCommit, see
    `CodeCommit Resources and
    Operations <https://docs.aws.amazon.com/codecommit/latest/userguide/auth-and-access-control-iam-access-control-identity-based.html#arn-formats>`__
    in the AWS CodeCommit User Guide.
    """


class RestrictedSourceFileException(ServiceException):
    """The commit cannot be created because one of the changes specifies
    copying or moving a .gitkeep file.
    """


class RevisionIdRequiredException(ServiceException):
    """A revision ID is required, but was not provided."""


class RevisionNotCurrentException(ServiceException):
    """The revision ID provided in the request does not match the current
    revision ID. Use GetPullRequest to retrieve the current revision ID.
    """


class SameFileContentException(ServiceException):
    """The file was not added or updated because the content of the file is
    exactly the same as the content of that file in the repository and
    branch that you specified.
    """


class SamePathRequestException(ServiceException):
    """The commit cannot be created because one or more changes in this commit
    duplicate actions in the same file path. For example, you cannot make
    the same delete request to the same file in the same file path twice, or
    make a delete request and a move request to the same file as part of the
    same commit.
    """


class SourceAndDestinationAreSameException(ServiceException):
    """The source branch and destination branch for the pull request are the
    same. You must specify different branches for the source and
    destination.
    """


class SourceFileOrContentRequiredException(ServiceException):
    """The commit cannot be created because no source files or file content
    have been specified for the commit.
    """


class TagKeysListRequiredException(ServiceException):
    """A list of tag keys is required. The list cannot be empty or null."""


class TagPolicyException(ServiceException):
    """The tag policy is not valid."""


class TagsMapRequiredException(ServiceException):
    """A map of tags is required."""


class TargetRequiredException(ServiceException):
    """A pull request target is required. It cannot be empty or null. A pull
    request target must contain the full values for the repository name,
    source branch, and destination branch for the pull request.
    """


class TargetsRequiredException(ServiceException):
    """An array of target objects is required. It cannot be empty or null."""


class TipOfSourceReferenceIsDifferentException(ServiceException):
    """The tip of the source branch in the destination repository does not
    match the tip of the source branch specified in your request. The pull
    request might have been updated. Make sure that you have the latest
    changes.
    """


class TipsDivergenceExceededException(ServiceException):
    """The divergence between the tips of the provided commit specifiers is too
    great to determine whether there might be any merge conflicts. Locally
    compare the specifiers using ``git diff`` or a diff tool.
    """


class TitleRequiredException(ServiceException):
    """A pull request title is required. It cannot be empty or null."""


class TooManyTagsException(ServiceException):
    """The maximum number of tags for an AWS CodeCommit resource has been
    exceeded.
    """


class Approval(TypedDict, total=False):
    """Returns information about a specific approval on a pull request."""

    userArn: Optional[Arn]
    approvalState: Optional[ApprovalState]


ApprovalList = List[Approval]


class OriginApprovalRuleTemplate(TypedDict, total=False):
    """Returns information about the template that created the approval rule
    for a pull request.
    """

    approvalRuleTemplateId: Optional[ApprovalRuleTemplateId]
    approvalRuleTemplateName: Optional[ApprovalRuleTemplateName]


CreationDate = datetime
LastModifiedDate = datetime


class ApprovalRule(TypedDict, total=False):
    """Returns information about an approval rule."""

    approvalRuleId: Optional[ApprovalRuleId]
    approvalRuleName: Optional[ApprovalRuleName]
    approvalRuleContent: Optional[ApprovalRuleContent]
    ruleContentSha256: Optional[RuleContentSha256]
    lastModifiedDate: Optional[LastModifiedDate]
    creationDate: Optional[CreationDate]
    lastModifiedUser: Optional[Arn]
    originApprovalRuleTemplate: Optional[OriginApprovalRuleTemplate]


class ApprovalRuleEventMetadata(TypedDict, total=False):
    """Returns information about an event for an approval rule."""

    approvalRuleName: Optional[ApprovalRuleName]
    approvalRuleId: Optional[ApprovalRuleId]
    approvalRuleContent: Optional[ApprovalRuleContent]


class ApprovalRuleOverriddenEventMetadata(TypedDict, total=False):
    """Returns information about an override event for approval rules for a
    pull request.
    """

    revisionId: Optional[RevisionId]
    overrideStatus: Optional[OverrideStatus]


class ApprovalRuleTemplate(TypedDict, total=False):
    """Returns information about an approval rule template."""

    approvalRuleTemplateId: Optional[ApprovalRuleTemplateId]
    approvalRuleTemplateName: Optional[ApprovalRuleTemplateName]
    approvalRuleTemplateDescription: Optional[ApprovalRuleTemplateDescription]
    approvalRuleTemplateContent: Optional[ApprovalRuleTemplateContent]
    ruleContentSha256: Optional[RuleContentSha256]
    lastModifiedDate: Optional[LastModifiedDate]
    creationDate: Optional[CreationDate]
    lastModifiedUser: Optional[Arn]


ApprovalRuleTemplateNameList = List[ApprovalRuleTemplateName]
ApprovalRulesList = List[ApprovalRule]
ApprovalRulesNotSatisfiedList = List[ApprovalRuleName]
ApprovalRulesSatisfiedList = List[ApprovalRuleName]


class ApprovalStateChangedEventMetadata(TypedDict, total=False):
    """Returns information about a change in the approval state for a pull
    request.
    """

    revisionId: Optional[RevisionId]
    approvalStatus: Optional[ApprovalState]


class AssociateApprovalRuleTemplateWithRepositoryInput(ServiceRequest):
    approvalRuleTemplateName: ApprovalRuleTemplateName
    repositoryName: RepositoryName


class BatchAssociateApprovalRuleTemplateWithRepositoriesError(TypedDict, total=False):
    """Returns information about errors in a
    BatchAssociateApprovalRuleTemplateWithRepositories operation.
    """

    repositoryName: Optional[RepositoryName]
    errorCode: Optional[ErrorCode]
    errorMessage: Optional[ErrorMessage]


BatchAssociateApprovalRuleTemplateWithRepositoriesErrorsList = List[
    BatchAssociateApprovalRuleTemplateWithRepositoriesError
]
RepositoryNameList = List[RepositoryName]


class BatchAssociateApprovalRuleTemplateWithRepositoriesInput(ServiceRequest):
    approvalRuleTemplateName: ApprovalRuleTemplateName
    repositoryNames: RepositoryNameList


class BatchAssociateApprovalRuleTemplateWithRepositoriesOutput(TypedDict, total=False):
    associatedRepositoryNames: RepositoryNameList
    errors: BatchAssociateApprovalRuleTemplateWithRepositoriesErrorsList


class BatchDescribeMergeConflictsError(TypedDict, total=False):
    """Returns information about errors in a BatchDescribeMergeConflicts
    operation.
    """

    filePath: Path
    exceptionName: ExceptionName
    message: Message


BatchDescribeMergeConflictsErrors = List[BatchDescribeMergeConflictsError]
FilePaths = List[Path]


class BatchDescribeMergeConflictsInput(ServiceRequest):
    repositoryName: RepositoryName
    destinationCommitSpecifier: CommitName
    sourceCommitSpecifier: CommitName
    mergeOption: MergeOptionTypeEnum
    maxMergeHunks: Optional[MaxResults]
    maxConflictFiles: Optional[MaxResults]
    filePaths: Optional[FilePaths]
    conflictDetailLevel: Optional[ConflictDetailLevelTypeEnum]
    conflictResolutionStrategy: Optional[ConflictResolutionStrategyTypeEnum]
    nextToken: Optional[NextToken]


class MergeHunkDetail(TypedDict, total=False):
    """Information about the details of a merge hunk that contains a conflict
    in a merge or pull request operation.
    """

    startLine: Optional[LineNumber]
    endLine: Optional[LineNumber]
    hunkContent: Optional[HunkContent]


class MergeHunk(TypedDict, total=False):
    """Information about merge hunks in a merge or pull request operation."""

    isConflict: Optional[IsHunkConflict]
    source: Optional[MergeHunkDetail]
    destination: Optional[MergeHunkDetail]
    base: Optional[MergeHunkDetail]


MergeHunks = List[MergeHunk]


class MergeOperations(TypedDict, total=False):
    """Information about the file operation conflicts in a merge operation."""

    source: Optional[ChangeTypeEnum]
    destination: Optional[ChangeTypeEnum]


class IsBinaryFile(TypedDict, total=False):
    """Information about whether a file is binary or textual in a merge or pull
    request operation.
    """

    source: Optional[CapitalBoolean]
    destination: Optional[CapitalBoolean]
    base: Optional[CapitalBoolean]


class ObjectTypes(TypedDict, total=False):
    """Information about the type of an object in a merge operation."""

    source: Optional[ObjectTypeEnum]
    destination: Optional[ObjectTypeEnum]
    base: Optional[ObjectTypeEnum]


class FileModes(TypedDict, total=False):
    """Information about file modes in a merge or pull request."""

    source: Optional[FileModeTypeEnum]
    destination: Optional[FileModeTypeEnum]
    base: Optional[FileModeTypeEnum]


FileSize = int


class FileSizes(TypedDict, total=False):
    """Information about the size of files in a merge or pull request."""

    source: Optional[FileSize]
    destination: Optional[FileSize]
    base: Optional[FileSize]


class ConflictMetadata(TypedDict, total=False):
    """Information about the metadata for a conflict in a merge operation."""

    filePath: Optional[Path]
    fileSizes: Optional[FileSizes]
    fileModes: Optional[FileModes]
    objectTypes: Optional[ObjectTypes]
    numberOfConflicts: Optional[NumberOfConflicts]
    isBinaryFile: Optional[IsBinaryFile]
    contentConflict: Optional[IsContentConflict]
    fileModeConflict: Optional[IsFileModeConflict]
    objectTypeConflict: Optional[IsObjectTypeConflict]
    mergeOperations: Optional[MergeOperations]


class Conflict(TypedDict, total=False):
    """Information about conflicts in a merge operation."""

    conflictMetadata: Optional[ConflictMetadata]
    mergeHunks: Optional[MergeHunks]


Conflicts = List[Conflict]


class BatchDescribeMergeConflictsOutput(TypedDict, total=False):
    conflicts: Conflicts
    nextToken: Optional[NextToken]
    errors: Optional[BatchDescribeMergeConflictsErrors]
    destinationCommitId: ObjectId
    sourceCommitId: ObjectId
    baseCommitId: Optional[ObjectId]


class BatchDisassociateApprovalRuleTemplateFromRepositoriesError(TypedDict, total=False):
    """Returns information about errors in a
    BatchDisassociateApprovalRuleTemplateFromRepositories operation.
    """

    repositoryName: Optional[RepositoryName]
    errorCode: Optional[ErrorCode]
    errorMessage: Optional[ErrorMessage]


BatchDisassociateApprovalRuleTemplateFromRepositoriesErrorsList = List[
    BatchDisassociateApprovalRuleTemplateFromRepositoriesError
]


class BatchDisassociateApprovalRuleTemplateFromRepositoriesInput(ServiceRequest):
    approvalRuleTemplateName: ApprovalRuleTemplateName
    repositoryNames: RepositoryNameList


class BatchDisassociateApprovalRuleTemplateFromRepositoriesOutput(TypedDict, total=False):
    disassociatedRepositoryNames: RepositoryNameList
    errors: BatchDisassociateApprovalRuleTemplateFromRepositoriesErrorsList


class BatchGetCommitsError(TypedDict, total=False):
    """Returns information about errors in a BatchGetCommits operation."""

    commitId: Optional[ObjectId]
    errorCode: Optional[ErrorCode]
    errorMessage: Optional[ErrorMessage]


BatchGetCommitsErrorsList = List[BatchGetCommitsError]
CommitIdsInputList = List[ObjectId]


class BatchGetCommitsInput(ServiceRequest):
    commitIds: CommitIdsInputList
    repositoryName: RepositoryName


class UserInfo(TypedDict, total=False):
    """Information about the user who made a specified commit."""

    name: Optional[Name]
    email: Optional[Email]
    date: Optional[Date]


ParentList = List[ObjectId]


class Commit(TypedDict, total=False):
    """Returns information about a specific commit."""

    commitId: Optional[ObjectId]
    treeId: Optional[ObjectId]
    parents: Optional[ParentList]
    message: Optional[Message]
    author: Optional[UserInfo]
    committer: Optional[UserInfo]
    additionalData: Optional[AdditionalData]


CommitObjectsList = List[Commit]


class BatchGetCommitsOutput(TypedDict, total=False):
    commits: Optional[CommitObjectsList]
    errors: Optional[BatchGetCommitsErrorsList]


class BatchGetRepositoriesInput(ServiceRequest):
    """Represents the input of a batch get repositories operation."""

    repositoryNames: RepositoryNameList


RepositoryNotFoundList = List[RepositoryName]


class RepositoryMetadata(TypedDict, total=False):
    """Information about a repository."""

    accountId: Optional[AccountId]
    repositoryId: Optional[RepositoryId]
    repositoryName: Optional[RepositoryName]
    repositoryDescription: Optional[RepositoryDescription]
    defaultBranch: Optional[BranchName]
    lastModifiedDate: Optional[LastModifiedDate]
    creationDate: Optional[CreationDate]
    cloneUrlHttp: Optional[CloneUrlHttp]
    cloneUrlSsh: Optional[CloneUrlSsh]
    Arn: Optional[Arn]


RepositoryMetadataList = List[RepositoryMetadata]


class BatchGetRepositoriesOutput(TypedDict, total=False):
    """Represents the output of a batch get repositories operation."""

    repositories: Optional[RepositoryMetadataList]
    repositoriesNotFound: Optional[RepositoryNotFoundList]


class BlobMetadata(TypedDict, total=False):
    """Returns information about a specific Git blob object."""

    blobId: Optional[ObjectId]
    path: Optional[Path]
    mode: Optional[Mode]


class BranchInfo(TypedDict, total=False):
    """Returns information about a branch."""

    branchName: Optional[BranchName]
    commitId: Optional[CommitId]


BranchNameList = List[BranchName]
CallerReactions = List[ReactionValue]
ReactionCountsMap = Dict[ReactionValue, Count]


class Comment(TypedDict, total=False):
    """Returns information about a specific comment."""

    commentId: Optional[CommentId]
    content: Optional[Content]
    inReplyTo: Optional[CommentId]
    creationDate: Optional[CreationDate]
    lastModifiedDate: Optional[LastModifiedDate]
    authorArn: Optional[Arn]
    deleted: Optional[IsCommentDeleted]
    clientRequestToken: Optional[ClientRequestToken]
    callerReactions: Optional[CallerReactions]
    reactionCounts: Optional[ReactionCountsMap]


Comments = List[Comment]
Position = int


class Location(TypedDict, total=False):
    """Returns information about the location of a change or comment in the
    comparison between two commits or a pull request.
    """

    filePath: Optional[Path]
    filePosition: Optional[Position]
    relativeFileVersion: Optional[RelativeFileVersionEnum]


class CommentsForComparedCommit(TypedDict, total=False):
    """Returns information about comments on the comparison between two
    commits.
    """

    repositoryName: Optional[RepositoryName]
    beforeCommitId: Optional[CommitId]
    afterCommitId: Optional[CommitId]
    beforeBlobId: Optional[ObjectId]
    afterBlobId: Optional[ObjectId]
    location: Optional[Location]
    comments: Optional[Comments]


CommentsForComparedCommitData = List[CommentsForComparedCommit]


class CommentsForPullRequest(TypedDict, total=False):
    """Returns information about comments on a pull request."""

    pullRequestId: Optional[PullRequestId]
    repositoryName: Optional[RepositoryName]
    beforeCommitId: Optional[CommitId]
    afterCommitId: Optional[CommitId]
    beforeBlobId: Optional[ObjectId]
    afterBlobId: Optional[ObjectId]
    location: Optional[Location]
    comments: Optional[Comments]


CommentsForPullRequestData = List[CommentsForPullRequest]
ConflictMetadataList = List[ConflictMetadata]


class SetFileModeEntry(TypedDict, total=False):
    """Information about the file mode changes."""

    filePath: Path
    fileMode: FileModeTypeEnum


SetFileModeEntries = List[SetFileModeEntry]


class DeleteFileEntry(TypedDict, total=False):
    """A file that is deleted as part of a commit."""

    filePath: Path


DeleteFileEntries = List[DeleteFileEntry]
FileContent = bytes


class ReplaceContentEntry(TypedDict, total=False):
    """Information about a replacement content entry in the conflict of a merge
    or pull request operation.
    """

    filePath: Path
    replacementType: ReplacementTypeEnum
    content: Optional[FileContent]
    fileMode: Optional[FileModeTypeEnum]


ReplaceContentEntries = List[ReplaceContentEntry]


class ConflictResolution(TypedDict, total=False):
    """If AUTOMERGE is the conflict resolution strategy, a list of inputs to
    use when resolving conflicts during a merge.
    """

    replaceContents: Optional[ReplaceContentEntries]
    deleteFiles: Optional[DeleteFileEntries]
    setFileModes: Optional[SetFileModeEntries]


class CreateApprovalRuleTemplateInput(ServiceRequest):
    approvalRuleTemplateName: ApprovalRuleTemplateName
    approvalRuleTemplateContent: ApprovalRuleTemplateContent
    approvalRuleTemplateDescription: Optional[ApprovalRuleTemplateDescription]


class CreateApprovalRuleTemplateOutput(TypedDict, total=False):
    approvalRuleTemplate: ApprovalRuleTemplate


class CreateBranchInput(ServiceRequest):
    """Represents the input of a create branch operation."""

    repositoryName: RepositoryName
    branchName: BranchName
    commitId: CommitId


class SourceFileSpecifier(TypedDict, total=False):
    """Information about a source file that is part of changes made in a
    commit.
    """

    filePath: Path
    isMove: Optional[IsMove]


class PutFileEntry(TypedDict, total=False):
    """Information about a file added or updated as part of a commit."""

    filePath: Path
    fileMode: Optional[FileModeTypeEnum]
    fileContent: Optional[FileContent]
    sourceFile: Optional[SourceFileSpecifier]


PutFileEntries = List[PutFileEntry]


class CreateCommitInput(ServiceRequest):
    repositoryName: RepositoryName
    branchName: BranchName
    parentCommitId: Optional[CommitId]
    authorName: Optional[Name]
    email: Optional[Email]
    commitMessage: Optional[Message]
    keepEmptyFolders: Optional[KeepEmptyFolders]
    putFiles: Optional[PutFileEntries]
    deleteFiles: Optional[DeleteFileEntries]
    setFileModes: Optional[SetFileModeEntries]


class FileMetadata(TypedDict, total=False):
    """A file to be added, updated, or deleted as part of a commit."""

    absolutePath: Optional[Path]
    blobId: Optional[ObjectId]
    fileMode: Optional[FileModeTypeEnum]


FilesMetadata = List[FileMetadata]


class CreateCommitOutput(TypedDict, total=False):
    commitId: Optional[ObjectId]
    treeId: Optional[ObjectId]
    filesAdded: Optional[FilesMetadata]
    filesUpdated: Optional[FilesMetadata]
    filesDeleted: Optional[FilesMetadata]


class CreatePullRequestApprovalRuleInput(ServiceRequest):
    pullRequestId: PullRequestId
    approvalRuleName: ApprovalRuleName
    approvalRuleContent: ApprovalRuleContent


class CreatePullRequestApprovalRuleOutput(TypedDict, total=False):
    approvalRule: ApprovalRule


class Target(TypedDict, total=False):
    """Returns information about a target for a pull request."""

    repositoryName: RepositoryName
    sourceReference: ReferenceName
    destinationReference: Optional[ReferenceName]


TargetList = List[Target]


class CreatePullRequestInput(ServiceRequest):
    title: Title
    description: Optional[Description]
    targets: TargetList
    clientRequestToken: Optional[ClientRequestToken]


class MergeMetadata(TypedDict, total=False):
    """Returns information about a merge or potential merge between a source
    reference and a destination reference in a pull request.
    """

    isMerged: Optional[IsMerged]
    mergedBy: Optional[Arn]
    mergeCommitId: Optional[CommitId]
    mergeOption: Optional[MergeOptionTypeEnum]


class PullRequestTarget(TypedDict, total=False):
    """Returns information about a pull request target."""

    repositoryName: Optional[RepositoryName]
    sourceReference: Optional[ReferenceName]
    destinationReference: Optional[ReferenceName]
    destinationCommit: Optional[CommitId]
    sourceCommit: Optional[CommitId]
    mergeBase: Optional[CommitId]
    mergeMetadata: Optional[MergeMetadata]


PullRequestTargetList = List[PullRequestTarget]


class PullRequest(TypedDict, total=False):
    """Returns information about a pull request."""

    pullRequestId: Optional[PullRequestId]
    title: Optional[Title]
    description: Optional[Description]
    lastActivityDate: Optional[LastModifiedDate]
    creationDate: Optional[CreationDate]
    pullRequestStatus: Optional[PullRequestStatusEnum]
    authorArn: Optional[Arn]
    pullRequestTargets: Optional[PullRequestTargetList]
    clientRequestToken: Optional[ClientRequestToken]
    revisionId: Optional[RevisionId]
    approvalRules: Optional[ApprovalRulesList]


class CreatePullRequestOutput(TypedDict, total=False):
    pullRequest: PullRequest


TagsMap = Dict[TagKey, TagValue]


class CreateRepositoryInput(ServiceRequest):
    """Represents the input of a create repository operation."""

    repositoryName: RepositoryName
    repositoryDescription: Optional[RepositoryDescription]
    tags: Optional[TagsMap]


class CreateRepositoryOutput(TypedDict, total=False):
    """Represents the output of a create repository operation."""

    repositoryMetadata: Optional[RepositoryMetadata]


class CreateUnreferencedMergeCommitInput(ServiceRequest):
    repositoryName: RepositoryName
    sourceCommitSpecifier: CommitName
    destinationCommitSpecifier: CommitName
    mergeOption: MergeOptionTypeEnum
    conflictDetailLevel: Optional[ConflictDetailLevelTypeEnum]
    conflictResolutionStrategy: Optional[ConflictResolutionStrategyTypeEnum]
    authorName: Optional[Name]
    email: Optional[Email]
    commitMessage: Optional[Message]
    keepEmptyFolders: Optional[KeepEmptyFolders]
    conflictResolution: Optional[ConflictResolution]


class CreateUnreferencedMergeCommitOutput(TypedDict, total=False):
    commitId: Optional[ObjectId]
    treeId: Optional[ObjectId]


class DeleteApprovalRuleTemplateInput(ServiceRequest):
    approvalRuleTemplateName: ApprovalRuleTemplateName


class DeleteApprovalRuleTemplateOutput(TypedDict, total=False):
    approvalRuleTemplateId: ApprovalRuleTemplateId


class DeleteBranchInput(ServiceRequest):
    """Represents the input of a delete branch operation."""

    repositoryName: RepositoryName
    branchName: BranchName


class DeleteBranchOutput(TypedDict, total=False):
    """Represents the output of a delete branch operation."""

    deletedBranch: Optional[BranchInfo]


class DeleteCommentContentInput(ServiceRequest):
    commentId: CommentId


class DeleteCommentContentOutput(TypedDict, total=False):
    comment: Optional[Comment]


class DeleteFileInput(ServiceRequest):
    repositoryName: RepositoryName
    branchName: BranchName
    filePath: Path
    parentCommitId: CommitId
    keepEmptyFolders: Optional[KeepEmptyFolders]
    commitMessage: Optional[Message]
    name: Optional[Name]
    email: Optional[Email]


class DeleteFileOutput(TypedDict, total=False):
    commitId: ObjectId
    blobId: ObjectId
    treeId: ObjectId
    filePath: Path


class DeletePullRequestApprovalRuleInput(ServiceRequest):
    pullRequestId: PullRequestId
    approvalRuleName: ApprovalRuleName


class DeletePullRequestApprovalRuleOutput(TypedDict, total=False):
    approvalRuleId: ApprovalRuleId


class DeleteRepositoryInput(ServiceRequest):
    """Represents the input of a delete repository operation."""

    repositoryName: RepositoryName


class DeleteRepositoryOutput(TypedDict, total=False):
    """Represents the output of a delete repository operation."""

    repositoryId: Optional[RepositoryId]


class DescribeMergeConflictsInput(ServiceRequest):
    repositoryName: RepositoryName
    destinationCommitSpecifier: CommitName
    sourceCommitSpecifier: CommitName
    mergeOption: MergeOptionTypeEnum
    maxMergeHunks: Optional[MaxResults]
    filePath: Path
    conflictDetailLevel: Optional[ConflictDetailLevelTypeEnum]
    conflictResolutionStrategy: Optional[ConflictResolutionStrategyTypeEnum]
    nextToken: Optional[NextToken]


class DescribeMergeConflictsOutput(TypedDict, total=False):
    conflictMetadata: ConflictMetadata
    mergeHunks: MergeHunks
    nextToken: Optional[NextToken]
    destinationCommitId: ObjectId
    sourceCommitId: ObjectId
    baseCommitId: Optional[ObjectId]


class DescribePullRequestEventsInput(ServiceRequest):
    pullRequestId: PullRequestId
    pullRequestEventType: Optional[PullRequestEventType]
    actorArn: Optional[Arn]
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class PullRequestMergedStateChangedEventMetadata(TypedDict, total=False):
    """Returns information about the change in the merge state for a pull
    request event.
    """

    repositoryName: Optional[RepositoryName]
    destinationReference: Optional[ReferenceName]
    mergeMetadata: Optional[MergeMetadata]


class PullRequestSourceReferenceUpdatedEventMetadata(TypedDict, total=False):
    """Information about an update to the source branch of a pull request."""

    repositoryName: Optional[RepositoryName]
    beforeCommitId: Optional[CommitId]
    afterCommitId: Optional[CommitId]
    mergeBase: Optional[CommitId]


class PullRequestStatusChangedEventMetadata(TypedDict, total=False):
    """Information about a change to the status of a pull request."""

    pullRequestStatus: Optional[PullRequestStatusEnum]


class PullRequestCreatedEventMetadata(TypedDict, total=False):
    """Metadata about the pull request that is used when comparing the pull
    request source with its destination.
    """

    repositoryName: Optional[RepositoryName]
    sourceCommitId: Optional[CommitId]
    destinationCommitId: Optional[CommitId]
    mergeBase: Optional[CommitId]


EventDate = datetime


class PullRequestEvent(TypedDict, total=False):
    """Returns information about a pull request event."""

    pullRequestId: Optional[PullRequestId]
    eventDate: Optional[EventDate]
    pullRequestEventType: Optional[PullRequestEventType]
    actorArn: Optional[Arn]
    pullRequestCreatedEventMetadata: Optional[PullRequestCreatedEventMetadata]
    pullRequestStatusChangedEventMetadata: Optional[PullRequestStatusChangedEventMetadata]
    pullRequestSourceReferenceUpdatedEventMetadata: Optional[
        PullRequestSourceReferenceUpdatedEventMetadata
    ]
    pullRequestMergedStateChangedEventMetadata: Optional[PullRequestMergedStateChangedEventMetadata]
    approvalRuleEventMetadata: Optional[ApprovalRuleEventMetadata]
    approvalStateChangedEventMetadata: Optional[ApprovalStateChangedEventMetadata]
    approvalRuleOverriddenEventMetadata: Optional[ApprovalRuleOverriddenEventMetadata]


PullRequestEventList = List[PullRequestEvent]


class DescribePullRequestEventsOutput(TypedDict, total=False):
    pullRequestEvents: PullRequestEventList
    nextToken: Optional[NextToken]


class Difference(TypedDict, total=False):
    """Returns information about a set of differences for a commit specifier."""

    beforeBlob: Optional[BlobMetadata]
    afterBlob: Optional[BlobMetadata]
    changeType: Optional[ChangeTypeEnum]


DifferenceList = List[Difference]


class DisassociateApprovalRuleTemplateFromRepositoryInput(ServiceRequest):
    approvalRuleTemplateName: ApprovalRuleTemplateName
    repositoryName: RepositoryName


class EvaluatePullRequestApprovalRulesInput(ServiceRequest):
    pullRequestId: PullRequestId
    revisionId: RevisionId


class Evaluation(TypedDict, total=False):
    """Returns information about the approval rules applied to a pull request
    and whether conditions have been met.
    """

    approved: Optional[Approved]
    overridden: Optional[Overridden]
    approvalRulesSatisfied: Optional[ApprovalRulesSatisfiedList]
    approvalRulesNotSatisfied: Optional[ApprovalRulesNotSatisfiedList]


class EvaluatePullRequestApprovalRulesOutput(TypedDict, total=False):
    evaluation: Evaluation


class File(TypedDict, total=False):
    """Returns information about a file in a repository."""

    blobId: Optional[ObjectId]
    absolutePath: Optional[Path]
    relativePath: Optional[Path]
    fileMode: Optional[FileModeTypeEnum]


FileList = List[File]


class Folder(TypedDict, total=False):
    """Returns information about a folder in a repository."""

    treeId: Optional[ObjectId]
    absolutePath: Optional[Path]
    relativePath: Optional[Path]


FolderList = List[Folder]


class GetApprovalRuleTemplateInput(ServiceRequest):
    approvalRuleTemplateName: ApprovalRuleTemplateName


class GetApprovalRuleTemplateOutput(TypedDict, total=False):
    approvalRuleTemplate: ApprovalRuleTemplate


class GetBlobInput(ServiceRequest):
    """Represents the input of a get blob operation."""

    repositoryName: RepositoryName
    blobId: ObjectId


blob = bytes


class GetBlobOutput(TypedDict, total=False):
    """Represents the output of a get blob operation."""

    content: blob


class GetBranchInput(ServiceRequest):
    """Represents the input of a get branch operation."""

    repositoryName: Optional[RepositoryName]
    branchName: Optional[BranchName]


class GetBranchOutput(TypedDict, total=False):
    """Represents the output of a get branch operation."""

    branch: Optional[BranchInfo]


class GetCommentInput(ServiceRequest):
    commentId: CommentId


class GetCommentOutput(TypedDict, total=False):
    comment: Optional[Comment]


class GetCommentReactionsInput(ServiceRequest):
    commentId: CommentId
    reactionUserArn: Optional[Arn]
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


ReactionUsersList = List[Arn]


class ReactionValueFormats(TypedDict, total=False):
    """Information about the values for reactions to a comment. AWS CodeCommit
    supports a limited set of reactions.
    """

    emoji: Optional[ReactionEmoji]
    shortCode: Optional[ReactionShortCode]
    unicode: Optional[ReactionUnicode]


class ReactionForComment(TypedDict, total=False):
    """Information about the reaction values provided by users on a comment."""

    reaction: Optional[ReactionValueFormats]
    reactionUsers: Optional[ReactionUsersList]
    reactionsFromDeletedUsersCount: Optional[Count]


ReactionsForCommentList = List[ReactionForComment]


class GetCommentReactionsOutput(TypedDict, total=False):
    reactionsForComment: ReactionsForCommentList
    nextToken: Optional[NextToken]


class GetCommentsForComparedCommitInput(ServiceRequest):
    repositoryName: RepositoryName
    beforeCommitId: Optional[CommitId]
    afterCommitId: CommitId
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class GetCommentsForComparedCommitOutput(TypedDict, total=False):
    commentsForComparedCommitData: Optional[CommentsForComparedCommitData]
    nextToken: Optional[NextToken]


class GetCommentsForPullRequestInput(ServiceRequest):
    pullRequestId: PullRequestId
    repositoryName: Optional[RepositoryName]
    beforeCommitId: Optional[CommitId]
    afterCommitId: Optional[CommitId]
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class GetCommentsForPullRequestOutput(TypedDict, total=False):
    commentsForPullRequestData: Optional[CommentsForPullRequestData]
    nextToken: Optional[NextToken]


class GetCommitInput(ServiceRequest):
    """Represents the input of a get commit operation."""

    repositoryName: RepositoryName
    commitId: ObjectId


class GetCommitOutput(TypedDict, total=False):
    """Represents the output of a get commit operation."""

    commit: Commit


class GetDifferencesInput(ServiceRequest):
    repositoryName: RepositoryName
    beforeCommitSpecifier: Optional[CommitName]
    afterCommitSpecifier: CommitName
    beforePath: Optional[Path]
    afterPath: Optional[Path]
    MaxResults: Optional[Limit]
    NextToken: Optional[NextToken]


class GetDifferencesOutput(TypedDict, total=False):
    differences: Optional[DifferenceList]
    NextToken: Optional[NextToken]


class GetFileInput(ServiceRequest):
    repositoryName: RepositoryName
    commitSpecifier: Optional[CommitName]
    filePath: Path


ObjectSize = int


class GetFileOutput(TypedDict, total=False):
    commitId: ObjectId
    blobId: ObjectId
    filePath: Path
    fileMode: FileModeTypeEnum
    fileSize: ObjectSize
    fileContent: FileContent


class GetFolderInput(ServiceRequest):
    repositoryName: RepositoryName
    commitSpecifier: Optional[CommitName]
    folderPath: Path


class SubModule(TypedDict, total=False):
    """Returns information about a submodule reference in a repository folder."""

    commitId: Optional[ObjectId]
    absolutePath: Optional[Path]
    relativePath: Optional[Path]


SubModuleList = List[SubModule]


class SymbolicLink(TypedDict, total=False):
    """Returns information about a symbolic link in a repository folder."""

    blobId: Optional[ObjectId]
    absolutePath: Optional[Path]
    relativePath: Optional[Path]
    fileMode: Optional[FileModeTypeEnum]


SymbolicLinkList = List[SymbolicLink]


class GetFolderOutput(TypedDict, total=False):
    commitId: ObjectId
    folderPath: Path
    treeId: Optional[ObjectId]
    subFolders: Optional[FolderList]
    files: Optional[FileList]
    symbolicLinks: Optional[SymbolicLinkList]
    subModules: Optional[SubModuleList]


class GetMergeCommitInput(ServiceRequest):
    repositoryName: RepositoryName
    sourceCommitSpecifier: CommitName
    destinationCommitSpecifier: CommitName
    conflictDetailLevel: Optional[ConflictDetailLevelTypeEnum]
    conflictResolutionStrategy: Optional[ConflictResolutionStrategyTypeEnum]


class GetMergeCommitOutput(TypedDict, total=False):
    sourceCommitId: Optional[ObjectId]
    destinationCommitId: Optional[ObjectId]
    baseCommitId: Optional[ObjectId]
    mergedCommitId: Optional[ObjectId]


class GetMergeConflictsInput(ServiceRequest):
    repositoryName: RepositoryName
    destinationCommitSpecifier: CommitName
    sourceCommitSpecifier: CommitName
    mergeOption: MergeOptionTypeEnum
    conflictDetailLevel: Optional[ConflictDetailLevelTypeEnum]
    maxConflictFiles: Optional[MaxResults]
    conflictResolutionStrategy: Optional[ConflictResolutionStrategyTypeEnum]
    nextToken: Optional[NextToken]


class GetMergeConflictsOutput(TypedDict, total=False):
    mergeable: IsMergeable
    destinationCommitId: ObjectId
    sourceCommitId: ObjectId
    baseCommitId: Optional[ObjectId]
    conflictMetadataList: ConflictMetadataList
    nextToken: Optional[NextToken]


class GetMergeOptionsInput(ServiceRequest):
    repositoryName: RepositoryName
    sourceCommitSpecifier: CommitName
    destinationCommitSpecifier: CommitName
    conflictDetailLevel: Optional[ConflictDetailLevelTypeEnum]
    conflictResolutionStrategy: Optional[ConflictResolutionStrategyTypeEnum]


MergeOptions = List[MergeOptionTypeEnum]


class GetMergeOptionsOutput(TypedDict, total=False):
    mergeOptions: MergeOptions
    sourceCommitId: ObjectId
    destinationCommitId: ObjectId
    baseCommitId: ObjectId


class GetPullRequestApprovalStatesInput(ServiceRequest):
    pullRequestId: PullRequestId
    revisionId: RevisionId


class GetPullRequestApprovalStatesOutput(TypedDict, total=False):
    approvals: Optional[ApprovalList]


class GetPullRequestInput(ServiceRequest):
    pullRequestId: PullRequestId


class GetPullRequestOutput(TypedDict, total=False):
    pullRequest: PullRequest


class GetPullRequestOverrideStateInput(ServiceRequest):
    pullRequestId: PullRequestId
    revisionId: RevisionId


class GetPullRequestOverrideStateOutput(TypedDict, total=False):
    overridden: Optional[Overridden]
    overrider: Optional[Arn]


class GetRepositoryInput(ServiceRequest):
    """Represents the input of a get repository operation."""

    repositoryName: RepositoryName


class GetRepositoryOutput(TypedDict, total=False):
    """Represents the output of a get repository operation."""

    repositoryMetadata: Optional[RepositoryMetadata]


class GetRepositoryTriggersInput(ServiceRequest):
    """Represents the input of a get repository triggers operation."""

    repositoryName: RepositoryName


RepositoryTriggerEventList = List[RepositoryTriggerEventEnum]


class RepositoryTrigger(TypedDict, total=False):
    """Information about a trigger for a repository."""

    name: RepositoryTriggerName
    destinationArn: Arn
    customData: Optional[RepositoryTriggerCustomData]
    branches: Optional[BranchNameList]
    events: RepositoryTriggerEventList


RepositoryTriggersList = List[RepositoryTrigger]


class GetRepositoryTriggersOutput(TypedDict, total=False):
    """Represents the output of a get repository triggers operation."""

    configurationId: Optional[RepositoryTriggersConfigurationId]
    triggers: Optional[RepositoryTriggersList]


class ListApprovalRuleTemplatesInput(ServiceRequest):
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class ListApprovalRuleTemplatesOutput(TypedDict, total=False):
    approvalRuleTemplateNames: Optional[ApprovalRuleTemplateNameList]
    nextToken: Optional[NextToken]


class ListAssociatedApprovalRuleTemplatesForRepositoryInput(ServiceRequest):
    repositoryName: RepositoryName
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class ListAssociatedApprovalRuleTemplatesForRepositoryOutput(TypedDict, total=False):
    approvalRuleTemplateNames: Optional[ApprovalRuleTemplateNameList]
    nextToken: Optional[NextToken]


class ListBranchesInput(ServiceRequest):
    """Represents the input of a list branches operation."""

    repositoryName: RepositoryName
    nextToken: Optional[NextToken]


class ListBranchesOutput(TypedDict, total=False):
    """Represents the output of a list branches operation."""

    branches: Optional[BranchNameList]
    nextToken: Optional[NextToken]


class ListPullRequestsInput(ServiceRequest):
    repositoryName: RepositoryName
    authorArn: Optional[Arn]
    pullRequestStatus: Optional[PullRequestStatusEnum]
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


PullRequestIdList = List[PullRequestId]


class ListPullRequestsOutput(TypedDict, total=False):
    pullRequestIds: PullRequestIdList
    nextToken: Optional[NextToken]


class ListRepositoriesForApprovalRuleTemplateInput(ServiceRequest):
    approvalRuleTemplateName: ApprovalRuleTemplateName
    nextToken: Optional[NextToken]
    maxResults: Optional[MaxResults]


class ListRepositoriesForApprovalRuleTemplateOutput(TypedDict, total=False):
    repositoryNames: Optional[RepositoryNameList]
    nextToken: Optional[NextToken]


class ListRepositoriesInput(ServiceRequest):
    """Represents the input of a list repositories operation."""

    nextToken: Optional[NextToken]
    sortBy: Optional[SortByEnum]
    order: Optional[OrderEnum]


class RepositoryNameIdPair(TypedDict, total=False):
    """Information about a repository name and ID."""

    repositoryName: Optional[RepositoryName]
    repositoryId: Optional[RepositoryId]


RepositoryNameIdPairList = List[RepositoryNameIdPair]


class ListRepositoriesOutput(TypedDict, total=False):
    """Represents the output of a list repositories operation."""

    repositories: Optional[RepositoryNameIdPairList]
    nextToken: Optional[NextToken]


class ListTagsForResourceInput(ServiceRequest):
    resourceArn: ResourceArn
    nextToken: Optional[NextToken]


class ListTagsForResourceOutput(TypedDict, total=False):
    tags: Optional[TagsMap]
    nextToken: Optional[NextToken]


class MergeBranchesByFastForwardInput(ServiceRequest):
    repositoryName: RepositoryName
    sourceCommitSpecifier: CommitName
    destinationCommitSpecifier: CommitName
    targetBranch: Optional[BranchName]


class MergeBranchesByFastForwardOutput(TypedDict, total=False):
    commitId: Optional[ObjectId]
    treeId: Optional[ObjectId]


class MergeBranchesBySquashInput(ServiceRequest):
    repositoryName: RepositoryName
    sourceCommitSpecifier: CommitName
    destinationCommitSpecifier: CommitName
    targetBranch: Optional[BranchName]
    conflictDetailLevel: Optional[ConflictDetailLevelTypeEnum]
    conflictResolutionStrategy: Optional[ConflictResolutionStrategyTypeEnum]
    authorName: Optional[Name]
    email: Optional[Email]
    commitMessage: Optional[Message]
    keepEmptyFolders: Optional[KeepEmptyFolders]
    conflictResolution: Optional[ConflictResolution]


class MergeBranchesBySquashOutput(TypedDict, total=False):
    commitId: Optional[ObjectId]
    treeId: Optional[ObjectId]


class MergeBranchesByThreeWayInput(ServiceRequest):
    repositoryName: RepositoryName
    sourceCommitSpecifier: CommitName
    destinationCommitSpecifier: CommitName
    targetBranch: Optional[BranchName]
    conflictDetailLevel: Optional[ConflictDetailLevelTypeEnum]
    conflictResolutionStrategy: Optional[ConflictResolutionStrategyTypeEnum]
    authorName: Optional[Name]
    email: Optional[Email]
    commitMessage: Optional[Message]
    keepEmptyFolders: Optional[KeepEmptyFolders]
    conflictResolution: Optional[ConflictResolution]


class MergeBranchesByThreeWayOutput(TypedDict, total=False):
    commitId: Optional[ObjectId]
    treeId: Optional[ObjectId]


class MergePullRequestByFastForwardInput(ServiceRequest):
    pullRequestId: PullRequestId
    repositoryName: RepositoryName
    sourceCommitId: Optional[ObjectId]


class MergePullRequestByFastForwardOutput(TypedDict, total=False):
    pullRequest: Optional[PullRequest]


class MergePullRequestBySquashInput(ServiceRequest):
    pullRequestId: PullRequestId
    repositoryName: RepositoryName
    sourceCommitId: Optional[ObjectId]
    conflictDetailLevel: Optional[ConflictDetailLevelTypeEnum]
    conflictResolutionStrategy: Optional[ConflictResolutionStrategyTypeEnum]
    commitMessage: Optional[Message]
    authorName: Optional[Name]
    email: Optional[Email]
    keepEmptyFolders: Optional[KeepEmptyFolders]
    conflictResolution: Optional[ConflictResolution]


class MergePullRequestBySquashOutput(TypedDict, total=False):
    pullRequest: Optional[PullRequest]


class MergePullRequestByThreeWayInput(ServiceRequest):
    pullRequestId: PullRequestId
    repositoryName: RepositoryName
    sourceCommitId: Optional[ObjectId]
    conflictDetailLevel: Optional[ConflictDetailLevelTypeEnum]
    conflictResolutionStrategy: Optional[ConflictResolutionStrategyTypeEnum]
    commitMessage: Optional[Message]
    authorName: Optional[Name]
    email: Optional[Email]
    keepEmptyFolders: Optional[KeepEmptyFolders]
    conflictResolution: Optional[ConflictResolution]


class MergePullRequestByThreeWayOutput(TypedDict, total=False):
    pullRequest: Optional[PullRequest]


class OverridePullRequestApprovalRulesInput(ServiceRequest):
    pullRequestId: PullRequestId
    revisionId: RevisionId
    overrideStatus: OverrideStatus


class PostCommentForComparedCommitInput(ServiceRequest):
    repositoryName: RepositoryName
    beforeCommitId: Optional[CommitId]
    afterCommitId: CommitId
    location: Optional[Location]
    content: Content
    clientRequestToken: Optional[ClientRequestToken]


class PostCommentForComparedCommitOutput(TypedDict, total=False):
    repositoryName: Optional[RepositoryName]
    beforeCommitId: Optional[CommitId]
    afterCommitId: Optional[CommitId]
    beforeBlobId: Optional[ObjectId]
    afterBlobId: Optional[ObjectId]
    location: Optional[Location]
    comment: Optional[Comment]


class PostCommentForPullRequestInput(ServiceRequest):
    pullRequestId: PullRequestId
    repositoryName: RepositoryName
    beforeCommitId: CommitId
    afterCommitId: CommitId
    location: Optional[Location]
    content: Content
    clientRequestToken: Optional[ClientRequestToken]


class PostCommentForPullRequestOutput(TypedDict, total=False):
    repositoryName: Optional[RepositoryName]
    pullRequestId: Optional[PullRequestId]
    beforeCommitId: Optional[CommitId]
    afterCommitId: Optional[CommitId]
    beforeBlobId: Optional[ObjectId]
    afterBlobId: Optional[ObjectId]
    location: Optional[Location]
    comment: Optional[Comment]


class PostCommentReplyInput(ServiceRequest):
    inReplyTo: CommentId
    clientRequestToken: Optional[ClientRequestToken]
    content: Content


class PostCommentReplyOutput(TypedDict, total=False):
    comment: Optional[Comment]


class PutCommentReactionInput(ServiceRequest):
    commentId: CommentId
    reactionValue: ReactionValue


class PutFileInput(ServiceRequest):
    repositoryName: RepositoryName
    branchName: BranchName
    fileContent: FileContent
    filePath: Path
    fileMode: Optional[FileModeTypeEnum]
    parentCommitId: Optional[CommitId]
    commitMessage: Optional[Message]
    name: Optional[Name]
    email: Optional[Email]


class PutFileOutput(TypedDict, total=False):
    commitId: ObjectId
    blobId: ObjectId
    treeId: ObjectId


class PutRepositoryTriggersInput(ServiceRequest):
    """Represents the input of a put repository triggers operation."""

    repositoryName: RepositoryName
    triggers: RepositoryTriggersList


class PutRepositoryTriggersOutput(TypedDict, total=False):
    """Represents the output of a put repository triggers operation."""

    configurationId: Optional[RepositoryTriggersConfigurationId]


class RepositoryTriggerExecutionFailure(TypedDict, total=False):
    """A trigger failed to run."""

    trigger: Optional[RepositoryTriggerName]
    failureMessage: Optional[RepositoryTriggerExecutionFailureMessage]


RepositoryTriggerExecutionFailureList = List[RepositoryTriggerExecutionFailure]
RepositoryTriggerNameList = List[RepositoryTriggerName]
TagKeysList = List[TagKey]


class TagResourceInput(ServiceRequest):
    resourceArn: ResourceArn
    tags: TagsMap


class TestRepositoryTriggersInput(ServiceRequest):
    """Represents the input of a test repository triggers operation."""

    repositoryName: RepositoryName
    triggers: RepositoryTriggersList


class TestRepositoryTriggersOutput(TypedDict, total=False):
    """Represents the output of a test repository triggers operation."""

    successfulExecutions: Optional[RepositoryTriggerNameList]
    failedExecutions: Optional[RepositoryTriggerExecutionFailureList]


class UntagResourceInput(ServiceRequest):
    resourceArn: ResourceArn
    tagKeys: TagKeysList


class UpdateApprovalRuleTemplateContentInput(ServiceRequest):
    approvalRuleTemplateName: ApprovalRuleTemplateName
    newRuleContent: ApprovalRuleTemplateContent
    existingRuleContentSha256: Optional[RuleContentSha256]


class UpdateApprovalRuleTemplateContentOutput(TypedDict, total=False):
    approvalRuleTemplate: ApprovalRuleTemplate


class UpdateApprovalRuleTemplateDescriptionInput(ServiceRequest):
    approvalRuleTemplateName: ApprovalRuleTemplateName
    approvalRuleTemplateDescription: ApprovalRuleTemplateDescription


class UpdateApprovalRuleTemplateDescriptionOutput(TypedDict, total=False):
    approvalRuleTemplate: ApprovalRuleTemplate


class UpdateApprovalRuleTemplateNameInput(ServiceRequest):
    oldApprovalRuleTemplateName: ApprovalRuleTemplateName
    newApprovalRuleTemplateName: ApprovalRuleTemplateName


class UpdateApprovalRuleTemplateNameOutput(TypedDict, total=False):
    approvalRuleTemplate: ApprovalRuleTemplate


class UpdateCommentInput(ServiceRequest):
    commentId: CommentId
    content: Content


class UpdateCommentOutput(TypedDict, total=False):
    comment: Optional[Comment]


class UpdateDefaultBranchInput(ServiceRequest):
    """Represents the input of an update default branch operation."""

    repositoryName: RepositoryName
    defaultBranchName: BranchName


class UpdatePullRequestApprovalRuleContentInput(ServiceRequest):
    pullRequestId: PullRequestId
    approvalRuleName: ApprovalRuleName
    existingRuleContentSha256: Optional[RuleContentSha256]
    newRuleContent: ApprovalRuleContent


class UpdatePullRequestApprovalRuleContentOutput(TypedDict, total=False):
    approvalRule: ApprovalRule


class UpdatePullRequestApprovalStateInput(ServiceRequest):
    pullRequestId: PullRequestId
    revisionId: RevisionId
    approvalState: ApprovalState


class UpdatePullRequestDescriptionInput(ServiceRequest):
    pullRequestId: PullRequestId
    description: Description


class UpdatePullRequestDescriptionOutput(TypedDict, total=False):
    pullRequest: PullRequest


class UpdatePullRequestStatusInput(ServiceRequest):
    pullRequestId: PullRequestId
    pullRequestStatus: PullRequestStatusEnum


class UpdatePullRequestStatusOutput(TypedDict, total=False):
    pullRequest: PullRequest


class UpdatePullRequestTitleInput(ServiceRequest):
    pullRequestId: PullRequestId
    title: Title


class UpdatePullRequestTitleOutput(TypedDict, total=False):
    pullRequest: PullRequest


class UpdateRepositoryDescriptionInput(ServiceRequest):
    """Represents the input of an update repository description operation."""

    repositoryName: RepositoryName
    repositoryDescription: Optional[RepositoryDescription]


class UpdateRepositoryNameInput(ServiceRequest):
    """Represents the input of an update repository description operation."""

    oldName: RepositoryName
    newName: RepositoryName


class CodecommitApi:

    service = "codecommit"
    version = "2015-04-13"

    @handler("AssociateApprovalRuleTemplateWithRepository")
    def associate_approval_rule_template_with_repository(
        self,
        context: RequestContext,
        approval_rule_template_name: ApprovalRuleTemplateName,
        repository_name: RepositoryName,
    ) -> None:
        """Creates an association between an approval rule template and a specified
        repository. Then, the next time a pull request is created in the
        repository where the destination reference (if specified) matches the
        destination reference (branch) for the pull request, an approval rule
        that matches the template conditions is automatically created for that
        pull request. If no destination references are specified in the
        template, an approval rule that matches the template contents is created
        for all pull requests in that repository.

        :param approval_rule_template_name: The name for the approval rule template.
        :param repository_name: The name of the repository that you want to associate with the template.
        :raises ApprovalRuleTemplateNameRequiredException:
        :raises InvalidApprovalRuleTemplateNameException:
        :raises ApprovalRuleTemplateDoesNotExistException:
        :raises MaximumRuleTemplatesAssociatedWithRepositoryException:
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("BatchAssociateApprovalRuleTemplateWithRepositories")
    def batch_associate_approval_rule_template_with_repositories(
        self,
        context: RequestContext,
        approval_rule_template_name: ApprovalRuleTemplateName,
        repository_names: RepositoryNameList,
    ) -> BatchAssociateApprovalRuleTemplateWithRepositoriesOutput:
        """Creates an association between an approval rule template and one or more
        specified repositories.

        :param approval_rule_template_name: The name of the template you want to associate with one or more
        repositories.
        :param repository_names: The names of the repositories you want to associate with the template.
        :returns: BatchAssociateApprovalRuleTemplateWithRepositoriesOutput
        :raises ApprovalRuleTemplateNameRequiredException:
        :raises InvalidApprovalRuleTemplateNameException:
        :raises ApprovalRuleTemplateDoesNotExistException:
        :raises RepositoryNamesRequiredException:
        :raises MaximumRepositoryNamesExceededException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("BatchDescribeMergeConflicts")
    def batch_describe_merge_conflicts(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        destination_commit_specifier: CommitName,
        source_commit_specifier: CommitName,
        merge_option: MergeOptionTypeEnum,
        max_merge_hunks: MaxResults = None,
        max_conflict_files: MaxResults = None,
        file_paths: FilePaths = None,
        conflict_detail_level: ConflictDetailLevelTypeEnum = None,
        conflict_resolution_strategy: ConflictResolutionStrategyTypeEnum = None,
        next_token: NextToken = None,
    ) -> BatchDescribeMergeConflictsOutput:
        """Returns information about one or more merge conflicts in the attempted
        merge of two commit specifiers using the squash or three-way merge
        strategy.

        :param repository_name: The name of the repository that contains the merge conflicts you want to
        review.
        :param destination_commit_specifier: The branch, tag, HEAD, or other fully qualified reference used to
        identify a commit (for example, a branch name or a full commit ID).
        :param source_commit_specifier: The branch, tag, HEAD, or other fully qualified reference used to
        identify a commit (for example, a branch name or a full commit ID).
        :param merge_option: The merge option or strategy you want to use to merge the code.
        :param max_merge_hunks: The maximum number of merge hunks to include in the output.
        :param max_conflict_files: The maximum number of files to include in the output.
        :param file_paths: The path of the target files used to describe the conflicts.
        :param conflict_detail_level: The level of conflict detail to use.
        :param conflict_resolution_strategy: Specifies which branch to use when resolving conflicts, or whether to
        attempt automatically merging two versions of a file.
        :param next_token: An enumeration token that, when provided in a request, returns the next
        batch of the results.
        :returns: BatchDescribeMergeConflictsOutput
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises MergeOptionRequiredException:
        :raises InvalidMergeOptionException:
        :raises InvalidContinuationTokenException:
        :raises CommitRequiredException:
        :raises CommitDoesNotExistException:
        :raises InvalidCommitException:
        :raises TipsDivergenceExceededException:
        :raises InvalidMaxConflictFilesException:
        :raises InvalidMaxMergeHunksException:
        :raises InvalidConflictDetailLevelException:
        :raises InvalidConflictResolutionStrategyException:
        :raises MaximumFileContentToLoadExceededException:
        :raises MaximumItemsToCompareExceededException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("BatchDisassociateApprovalRuleTemplateFromRepositories")
    def batch_disassociate_approval_rule_template_from_repositories(
        self,
        context: RequestContext,
        approval_rule_template_name: ApprovalRuleTemplateName,
        repository_names: RepositoryNameList,
    ) -> BatchDisassociateApprovalRuleTemplateFromRepositoriesOutput:
        """Removes the association between an approval rule template and one or
        more specified repositories.

        :param approval_rule_template_name: The name of the template that you want to disassociate from one or more
        repositories.
        :param repository_names: The repository names that you want to disassociate from the approval
        rule template.
        :returns: BatchDisassociateApprovalRuleTemplateFromRepositoriesOutput
        :raises ApprovalRuleTemplateNameRequiredException:
        :raises InvalidApprovalRuleTemplateNameException:
        :raises ApprovalRuleTemplateDoesNotExistException:
        :raises RepositoryNamesRequiredException:
        :raises MaximumRepositoryNamesExceededException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("BatchGetCommits")
    def batch_get_commits(
        self,
        context: RequestContext,
        commit_ids: CommitIdsInputList,
        repository_name: RepositoryName,
    ) -> BatchGetCommitsOutput:
        """Returns information about the contents of one or more commits in a
        repository.

        :param commit_ids: The full commit IDs of the commits to get information about.
        :param repository_name: The name of the repository that contains the commits.
        :returns: BatchGetCommitsOutput
        :raises CommitIdsListRequiredException:
        :raises CommitIdsLimitExceededException:
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("BatchGetRepositories")
    def batch_get_repositories(
        self, context: RequestContext, repository_names: RepositoryNameList
    ) -> BatchGetRepositoriesOutput:
        """Returns information about one or more repositories.

        The description field for a repository accepts all HTML characters and
        all valid Unicode characters. Applications that do not HTML-encode the
        description and display it in a webpage can expose users to potentially
        malicious code. Make sure that you HTML-encode the description field in
        any application that uses this API to display the repository description
        on a webpage.

        :param repository_names: The names of the repositories to get information about.
        :returns: BatchGetRepositoriesOutput
        :raises RepositoryNamesRequiredException:
        :raises MaximumRepositoryNamesExceededException:
        :raises InvalidRepositoryNameException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("CreateApprovalRuleTemplate")
    def create_approval_rule_template(
        self,
        context: RequestContext,
        approval_rule_template_name: ApprovalRuleTemplateName,
        approval_rule_template_content: ApprovalRuleTemplateContent,
        approval_rule_template_description: ApprovalRuleTemplateDescription = None,
    ) -> CreateApprovalRuleTemplateOutput:
        """Creates a template for approval rules that can then be associated with
        one or more repositories in your AWS account. When you associate a
        template with a repository, AWS CodeCommit creates an approval rule that
        matches the conditions of the template for all pull requests that meet
        the conditions of the template. For more information, see
        AssociateApprovalRuleTemplateWithRepository.

        :param approval_rule_template_name: The name of the approval rule template.
        :param approval_rule_template_content: The content of the approval rule that is created on pull requests in
        associated repositories.
        :param approval_rule_template_description: The description of the approval rule template.
        :returns: CreateApprovalRuleTemplateOutput
        :raises ApprovalRuleTemplateNameRequiredException:
        :raises InvalidApprovalRuleTemplateNameException:
        :raises ApprovalRuleTemplateNameAlreadyExistsException:
        :raises ApprovalRuleTemplateContentRequiredException:
        :raises InvalidApprovalRuleTemplateContentException:
        :raises InvalidApprovalRuleTemplateDescriptionException:
        :raises NumberOfRuleTemplatesExceededException:
        """
        raise NotImplementedError

    @handler("CreateBranch")
    def create_branch(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        branch_name: BranchName,
        commit_id: CommitId,
    ) -> None:
        """Creates a branch in a repository and points the branch to a commit.

        Calling the create branch operation does not set a repository's default
        branch. To do this, call the update default branch operation.

        :param repository_name: The name of the repository in which you want to create the new branch.
        :param branch_name: The name of the new branch to create.
        :param commit_id: The ID of the commit to point the new branch to.
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises BranchNameRequiredException:
        :raises BranchNameExistsException:
        :raises InvalidBranchNameException:
        :raises CommitIdRequiredException:
        :raises CommitDoesNotExistException:
        :raises InvalidCommitIdException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("CreateCommit")
    def create_commit(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        branch_name: BranchName,
        parent_commit_id: CommitId = None,
        author_name: Name = None,
        email: Email = None,
        commit_message: Message = None,
        keep_empty_folders: KeepEmptyFolders = None,
        put_files: PutFileEntries = None,
        delete_files: DeleteFileEntries = None,
        set_file_modes: SetFileModeEntries = None,
    ) -> CreateCommitOutput:
        """Creates a commit for a repository on the tip of a specified branch.

        :param repository_name: The name of the repository where you create the commit.
        :param branch_name: The name of the branch where you create the commit.
        :param parent_commit_id: The ID of the commit that is the parent of the commit you create.
        :param author_name: The name of the author who created the commit.
        :param email: The email address of the person who created the commit.
        :param commit_message: The commit message you want to include in the commit.
        :param keep_empty_folders: If the commit contains deletions, whether to keep a folder or folder
        structure if the changes leave the folders empty.
        :param put_files: The files to add or update in this commit.
        :param delete_files: The files to delete in this commit.
        :param set_file_modes: The file modes to update for files in this commit.
        :returns: CreateCommitOutput
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises ParentCommitIdRequiredException:
        :raises InvalidParentCommitIdException:
        :raises ParentCommitDoesNotExistException:
        :raises ParentCommitIdOutdatedException:
        :raises BranchNameRequiredException:
        :raises InvalidBranchNameException:
        :raises BranchDoesNotExistException:
        :raises BranchNameIsTagNameException:
        :raises FileEntryRequiredException:
        :raises MaximumFileEntriesExceededException:
        :raises PutFileEntryConflictException:
        :raises SourceFileOrContentRequiredException:
        :raises FileContentAndSourceFileSpecifiedException:
        :raises PathRequiredException:
        :raises InvalidPathException:
        :raises SamePathRequestException:
        :raises FileDoesNotExistException:
        :raises FileContentSizeLimitExceededException:
        :raises FolderContentSizeLimitExceededException:
        :raises InvalidDeletionParameterException:
        :raises RestrictedSourceFileException:
        :raises FileModeRequiredException:
        :raises InvalidFileModeException:
        :raises NameLengthExceededException:
        :raises InvalidEmailException:
        :raises CommitMessageLengthExceededException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        :raises NoChangeException:
        :raises FileNameConflictsWithDirectoryNameException:
        :raises DirectoryNameConflictsWithFileNameException:
        :raises FilePathConflictsWithSubmodulePathException:
        """
        raise NotImplementedError

    @handler("CreatePullRequest")
    def create_pull_request(
        self,
        context: RequestContext,
        title: Title,
        targets: TargetList,
        description: Description = None,
        client_request_token: ClientRequestToken = None,
    ) -> CreatePullRequestOutput:
        """Creates a pull request in the specified repository.

        :param title: The title of the pull request.
        :param targets: The targets for the pull request, including the source of the code to be
        reviewed (the source branch) and the destination where the creator of
        the pull request intends the code to be merged after the pull request is
        closed (the destination branch).
        :param description: A description of the pull request.
        :param client_request_token: A unique, client-generated idempotency token that, when provided in a
        request, ensures the request cannot be repeated with a changed
        parameter.
        :returns: CreatePullRequestOutput
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        :raises ClientRequestTokenRequiredException:
        :raises InvalidClientRequestTokenException:
        :raises IdempotencyParameterMismatchException:
        :raises ReferenceNameRequiredException:
        :raises InvalidReferenceNameException:
        :raises ReferenceDoesNotExistException:
        :raises ReferenceTypeNotSupportedException:
        :raises TitleRequiredException:
        :raises InvalidTitleException:
        :raises InvalidDescriptionException:
        :raises TargetsRequiredException:
        :raises InvalidTargetsException:
        :raises TargetRequiredException:
        :raises InvalidTargetException:
        :raises MultipleRepositoriesInPullRequestException:
        :raises MaximumOpenPullRequestsExceededException:
        :raises SourceAndDestinationAreSameException:
        """
        raise NotImplementedError

    @handler("CreatePullRequestApprovalRule")
    def create_pull_request_approval_rule(
        self,
        context: RequestContext,
        pull_request_id: PullRequestId,
        approval_rule_name: ApprovalRuleName,
        approval_rule_content: ApprovalRuleContent,
    ) -> CreatePullRequestApprovalRuleOutput:
        """Creates an approval rule for a pull request.

        :param pull_request_id: The system-generated ID of the pull request for which you want to create
        the approval rule.
        :param approval_rule_name: The name for the approval rule.
        :param approval_rule_content: The content of the approval rule, including the number of approvals
        needed and the structure of an approval pool defined for approvals, if
        any.
        :returns: CreatePullRequestApprovalRuleOutput
        :raises ApprovalRuleNameRequiredException:
        :raises InvalidApprovalRuleNameException:
        :raises ApprovalRuleNameAlreadyExistsException:
        :raises ApprovalRuleContentRequiredException:
        :raises InvalidApprovalRuleContentException:
        :raises NumberOfRulesExceededException:
        :raises PullRequestDoesNotExistException:
        :raises InvalidPullRequestIdException:
        :raises PullRequestIdRequiredException:
        :raises PullRequestAlreadyClosedException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("CreateRepository")
    def create_repository(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        repository_description: RepositoryDescription = None,
        tags: TagsMap = None,
    ) -> CreateRepositoryOutput:
        """Creates a new, empty repository.

        :param repository_name: The name of the new repository to be created.
        :param repository_description: A comment or description about the new repository.
        :param tags: One or more tag key-value pairs to use when tagging this repository.
        :returns: CreateRepositoryOutput
        :raises RepositoryNameExistsException:
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises InvalidRepositoryDescriptionException:
        :raises RepositoryLimitExceededException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        :raises InvalidTagsMapException:
        :raises TooManyTagsException:
        :raises InvalidSystemTagUsageException:
        :raises TagPolicyException:
        """
        raise NotImplementedError

    @handler("CreateUnreferencedMergeCommit")
    def create_unreferenced_merge_commit(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        source_commit_specifier: CommitName,
        destination_commit_specifier: CommitName,
        merge_option: MergeOptionTypeEnum,
        conflict_detail_level: ConflictDetailLevelTypeEnum = None,
        conflict_resolution_strategy: ConflictResolutionStrategyTypeEnum = None,
        author_name: Name = None,
        email: Email = None,
        commit_message: Message = None,
        keep_empty_folders: KeepEmptyFolders = None,
        conflict_resolution: ConflictResolution = None,
    ) -> CreateUnreferencedMergeCommitOutput:
        """Creates an unreferenced commit that represents the result of merging two
        branches using a specified merge strategy. This can help you determine
        the outcome of a potential merge. This API cannot be used with the
        fast-forward merge strategy because that strategy does not create a
        merge commit.

        This unreferenced merge commit can only be accessed using the GetCommit
        API or through git commands such as git fetch. To retrieve this commit,
        you must specify its commit ID or otherwise reference it.

        :param repository_name: The name of the repository where you want to create the unreferenced
        merge commit.
        :param source_commit_specifier: The branch, tag, HEAD, or other fully qualified reference used to
        identify a commit (for example, a branch name or a full commit ID).
        :param destination_commit_specifier: The branch, tag, HEAD, or other fully qualified reference used to
        identify a commit (for example, a branch name or a full commit ID).
        :param merge_option: The merge option or strategy you want to use to merge the code.
        :param conflict_detail_level: The level of conflict detail to use.
        :param conflict_resolution_strategy: Specifies which branch to use when resolving conflicts, or whether to
        attempt automatically merging two versions of a file.
        :param author_name: The name of the author who created the unreferenced commit.
        :param email: The email address for the person who created the unreferenced commit.
        :param commit_message: The commit message for the unreferenced commit.
        :param keep_empty_folders: If the commit contains deletions, whether to keep a folder or folder
        structure if the changes leave the folders empty.
        :param conflict_resolution: If AUTOMERGE is the conflict resolution strategy, a list of inputs to
        use when resolving conflicts during a merge.
        :returns: CreateUnreferencedMergeCommitOutput
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises TipsDivergenceExceededException:
        :raises CommitRequiredException:
        :raises InvalidCommitException:
        :raises CommitDoesNotExistException:
        :raises MergeOptionRequiredException:
        :raises InvalidMergeOptionException:
        :raises InvalidConflictDetailLevelException:
        :raises InvalidConflictResolutionStrategyException:
        :raises InvalidConflictResolutionException:
        :raises ManualMergeRequiredException:
        :raises MaximumConflictResolutionEntriesExceededException:
        :raises MultipleConflictResolutionEntriesException:
        :raises ReplacementTypeRequiredException:
        :raises InvalidReplacementTypeException:
        :raises ReplacementContentRequiredException:
        :raises InvalidReplacementContentException:
        :raises PathRequiredException:
        :raises InvalidPathException:
        :raises FileContentSizeLimitExceededException:
        :raises FolderContentSizeLimitExceededException:
        :raises MaximumFileContentToLoadExceededException:
        :raises MaximumItemsToCompareExceededException:
        :raises ConcurrentReferenceUpdateException:
        :raises FileModeRequiredException:
        :raises InvalidFileModeException:
        :raises NameLengthExceededException:
        :raises InvalidEmailException:
        :raises CommitMessageLengthExceededException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("DeleteApprovalRuleTemplate")
    def delete_approval_rule_template(
        self, context: RequestContext, approval_rule_template_name: ApprovalRuleTemplateName
    ) -> DeleteApprovalRuleTemplateOutput:
        """Deletes a specified approval rule template. Deleting a template does not
        remove approval rules on pull requests already created with the
        template.

        :param approval_rule_template_name: The name of the approval rule template to delete.
        :returns: DeleteApprovalRuleTemplateOutput
        :raises ApprovalRuleTemplateNameRequiredException:
        :raises InvalidApprovalRuleTemplateNameException:
        :raises ApprovalRuleTemplateInUseException:
        """
        raise NotImplementedError

    @handler("DeleteBranch")
    def delete_branch(
        self, context: RequestContext, repository_name: RepositoryName, branch_name: BranchName
    ) -> DeleteBranchOutput:
        """Deletes a branch from a repository, unless that branch is the default
        branch for the repository.

        :param repository_name: The name of the repository that contains the branch to be deleted.
        :param branch_name: The name of the branch to delete.
        :returns: DeleteBranchOutput
        :raises RepositoryNameRequiredException:
        :raises RepositoryDoesNotExistException:
        :raises InvalidRepositoryNameException:
        :raises BranchNameRequiredException:
        :raises InvalidBranchNameException:
        :raises DefaultBranchCannotBeDeletedException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("DeleteCommentContent")
    def delete_comment_content(
        self, context: RequestContext, comment_id: CommentId
    ) -> DeleteCommentContentOutput:
        """Deletes the content of a comment made on a change, file, or commit in a
        repository.

        :param comment_id: The unique, system-generated ID of the comment.
        :returns: DeleteCommentContentOutput
        :raises CommentDoesNotExistException:
        :raises CommentIdRequiredException:
        :raises InvalidCommentIdException:
        :raises CommentDeletedException:
        """
        raise NotImplementedError

    @handler("DeleteFile")
    def delete_file(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        branch_name: BranchName,
        file_path: Path,
        parent_commit_id: CommitId,
        keep_empty_folders: KeepEmptyFolders = None,
        commit_message: Message = None,
        name: Name = None,
        email: Email = None,
    ) -> DeleteFileOutput:
        """Deletes a specified file from a specified branch. A commit is created on
        the branch that contains the revision. The file still exists in the
        commits earlier to the commit that contains the deletion.

        :param repository_name: The name of the repository that contains the file to delete.
        :param branch_name: The name of the branch where the commit that deletes the file is made.
        :param file_path: The fully qualified path to the file that to be deleted, including the
        full name and extension of that file.
        :param parent_commit_id: The ID of the commit that is the tip of the branch where you want to
        create the commit that deletes the file.
        :param keep_empty_folders: If a file is the only object in the folder or directory, specifies
        whether to delete the folder or directory that contains the file.
        :param commit_message: The commit message you want to include as part of deleting the file.
        :param name: The name of the author of the commit that deletes the file.
        :param email: The email address for the commit that deletes the file.
        :returns: DeleteFileOutput
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises ParentCommitIdRequiredException:
        :raises InvalidParentCommitIdException:
        :raises ParentCommitDoesNotExistException:
        :raises ParentCommitIdOutdatedException:
        :raises PathRequiredException:
        :raises InvalidPathException:
        :raises FileDoesNotExistException:
        :raises BranchNameRequiredException:
        :raises InvalidBranchNameException:
        :raises BranchDoesNotExistException:
        :raises BranchNameIsTagNameException:
        :raises NameLengthExceededException:
        :raises InvalidEmailException:
        :raises CommitMessageLengthExceededException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("DeletePullRequestApprovalRule")
    def delete_pull_request_approval_rule(
        self,
        context: RequestContext,
        pull_request_id: PullRequestId,
        approval_rule_name: ApprovalRuleName,
    ) -> DeletePullRequestApprovalRuleOutput:
        """Deletes an approval rule from a specified pull request. Approval rules
        can be deleted from a pull request only if the pull request is open, and
        if the approval rule was created specifically for a pull request and not
        generated from an approval rule template associated with the repository
        where the pull request was created. You cannot delete an approval rule
        from a merged or closed pull request.

        :param pull_request_id: The system-generated ID of the pull request that contains the approval
        rule you want to delete.
        :param approval_rule_name: The name of the approval rule you want to delete.
        :returns: DeletePullRequestApprovalRuleOutput
        :raises PullRequestDoesNotExistException:
        :raises InvalidPullRequestIdException:
        :raises PullRequestIdRequiredException:
        :raises PullRequestAlreadyClosedException:
        :raises ApprovalRuleNameRequiredException:
        :raises InvalidApprovalRuleNameException:
        :raises CannotDeleteApprovalRuleFromTemplateException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("DeleteRepository")
    def delete_repository(
        self, context: RequestContext, repository_name: RepositoryName
    ) -> DeleteRepositoryOutput:
        """Deletes a repository. If a specified repository was already deleted, a
        null repository ID is returned.

        Deleting a repository also deletes all associated objects and metadata.
        After a repository is deleted, all future push calls to the deleted
        repository fail.

        :param repository_name: The name of the repository to delete.
        :returns: DeleteRepositoryOutput
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("DescribeMergeConflicts")
    def describe_merge_conflicts(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        destination_commit_specifier: CommitName,
        source_commit_specifier: CommitName,
        merge_option: MergeOptionTypeEnum,
        file_path: Path,
        max_merge_hunks: MaxResults = None,
        conflict_detail_level: ConflictDetailLevelTypeEnum = None,
        conflict_resolution_strategy: ConflictResolutionStrategyTypeEnum = None,
        next_token: NextToken = None,
    ) -> DescribeMergeConflictsOutput:
        """Returns information about one or more merge conflicts in the attempted
        merge of two commit specifiers using the squash or three-way merge
        strategy. If the merge option for the attempted merge is specified as
        FAST_FORWARD_MERGE, an exception is thrown.

        :param repository_name: The name of the repository where you want to get information about a
        merge conflict.
        :param destination_commit_specifier: The branch, tag, HEAD, or other fully qualified reference used to
        identify a commit (for example, a branch name or a full commit ID).
        :param source_commit_specifier: The branch, tag, HEAD, or other fully qualified reference used to
        identify a commit (for example, a branch name or a full commit ID).
        :param merge_option: The merge option or strategy you want to use to merge the code.
        :param file_path: The path of the target files used to describe the conflicts.
        :param max_merge_hunks: The maximum number of merge hunks to include in the output.
        :param conflict_detail_level: The level of conflict detail to use.
        :param conflict_resolution_strategy: Specifies which branch to use when resolving conflicts, or whether to
        attempt automatically merging two versions of a file.
        :param next_token: An enumeration token that, when provided in a request, returns the next
        batch of the results.
        :returns: DescribeMergeConflictsOutput
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises MergeOptionRequiredException:
        :raises InvalidMergeOptionException:
        :raises InvalidContinuationTokenException:
        :raises CommitRequiredException:
        :raises CommitDoesNotExistException:
        :raises InvalidCommitException:
        :raises TipsDivergenceExceededException:
        :raises PathRequiredException:
        :raises InvalidPathException:
        :raises FileDoesNotExistException:
        :raises InvalidMaxMergeHunksException:
        :raises InvalidConflictDetailLevelException:
        :raises InvalidConflictResolutionStrategyException:
        :raises MaximumFileContentToLoadExceededException:
        :raises MaximumItemsToCompareExceededException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("DescribePullRequestEvents")
    def describe_pull_request_events(
        self,
        context: RequestContext,
        pull_request_id: PullRequestId,
        pull_request_event_type: PullRequestEventType = None,
        actor_arn: Arn = None,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> DescribePullRequestEventsOutput:
        """Returns information about one or more pull request events.

        :param pull_request_id: The system-generated ID of the pull request.
        :param pull_request_event_type: Optional.
        :param actor_arn: The Amazon Resource Name (ARN) of the user whose actions resulted in the
        event.
        :param next_token: An enumeration token that, when provided in a request, returns the next
        batch of the results.
        :param max_results: A non-zero, non-negative integer used to limit the number of returned
        results.
        :returns: DescribePullRequestEventsOutput
        :raises PullRequestDoesNotExistException:
        :raises InvalidPullRequestIdException:
        :raises PullRequestIdRequiredException:
        :raises InvalidPullRequestEventTypeException:
        :raises InvalidActorArnException:
        :raises ActorDoesNotExistException:
        :raises InvalidMaxResultsException:
        :raises InvalidContinuationTokenException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("DisassociateApprovalRuleTemplateFromRepository")
    def disassociate_approval_rule_template_from_repository(
        self,
        context: RequestContext,
        approval_rule_template_name: ApprovalRuleTemplateName,
        repository_name: RepositoryName,
    ) -> None:
        """Removes the association between a template and a repository so that
        approval rules based on the template are not automatically created when
        pull requests are created in the specified repository. This does not
        delete any approval rules previously created for pull requests through
        the template association.

        :param approval_rule_template_name: The name of the approval rule template to disassociate from a specified
        repository.
        :param repository_name: The name of the repository you want to disassociate from the template.
        :raises ApprovalRuleTemplateNameRequiredException:
        :raises InvalidApprovalRuleTemplateNameException:
        :raises ApprovalRuleTemplateDoesNotExistException:
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("EvaluatePullRequestApprovalRules")
    def evaluate_pull_request_approval_rules(
        self, context: RequestContext, pull_request_id: PullRequestId, revision_id: RevisionId
    ) -> EvaluatePullRequestApprovalRulesOutput:
        """Evaluates whether a pull request has met all the conditions specified in
        its associated approval rules.

        :param pull_request_id: The system-generated ID of the pull request you want to evaluate.
        :param revision_id: The system-generated ID for the pull request revision.
        :returns: EvaluatePullRequestApprovalRulesOutput
        :raises PullRequestDoesNotExistException:
        :raises InvalidPullRequestIdException:
        :raises PullRequestIdRequiredException:
        :raises InvalidRevisionIdException:
        :raises RevisionIdRequiredException:
        :raises RevisionNotCurrentException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("GetApprovalRuleTemplate")
    def get_approval_rule_template(
        self, context: RequestContext, approval_rule_template_name: ApprovalRuleTemplateName
    ) -> GetApprovalRuleTemplateOutput:
        """Returns information about a specified approval rule template.

        :param approval_rule_template_name: The name of the approval rule template for which you want to get
        information.
        :returns: GetApprovalRuleTemplateOutput
        :raises ApprovalRuleTemplateNameRequiredException:
        :raises InvalidApprovalRuleTemplateNameException:
        :raises ApprovalRuleTemplateDoesNotExistException:
        """
        raise NotImplementedError

    @handler("GetBlob")
    def get_blob(
        self, context: RequestContext, repository_name: RepositoryName, blob_id: ObjectId
    ) -> GetBlobOutput:
        """Returns the base-64 encoded content of an individual blob in a
        repository.

        :param repository_name: The name of the repository that contains the blob.
        :param blob_id: The ID of the blob, which is its SHA-1 pointer.
        :returns: GetBlobOutput
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises BlobIdRequiredException:
        :raises InvalidBlobIdException:
        :raises BlobIdDoesNotExistException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        :raises FileTooLargeException:
        """
        raise NotImplementedError

    @handler("GetBranch")
    def get_branch(
        self,
        context: RequestContext,
        repository_name: RepositoryName = None,
        branch_name: BranchName = None,
    ) -> GetBranchOutput:
        """Returns information about a repository branch, including its name and
        the last commit ID.

        :param repository_name: The name of the repository that contains the branch for which you want
        to retrieve information.
        :param branch_name: The name of the branch for which you want to retrieve information.
        :returns: GetBranchOutput
        :raises RepositoryNameRequiredException:
        :raises RepositoryDoesNotExistException:
        :raises InvalidRepositoryNameException:
        :raises BranchNameRequiredException:
        :raises InvalidBranchNameException:
        :raises BranchDoesNotExistException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("GetComment")
    def get_comment(self, context: RequestContext, comment_id: CommentId) -> GetCommentOutput:
        """Returns the content of a comment made on a change, file, or commit in a
        repository.

        Reaction counts might include numbers from user identities who were
        deleted after the reaction was made. For a count of reactions from
        active identities, use GetCommentReactions.

        :param comment_id: The unique, system-generated ID of the comment.
        :returns: GetCommentOutput
        :raises CommentDoesNotExistException:
        :raises CommentDeletedException:
        :raises CommentIdRequiredException:
        :raises InvalidCommentIdException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("GetCommentReactions")
    def get_comment_reactions(
        self,
        context: RequestContext,
        comment_id: CommentId,
        reaction_user_arn: Arn = None,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> GetCommentReactionsOutput:
        """Returns information about reactions to a specified comment ID. Reactions
        from users who have been deleted will not be included in the count.

        :param comment_id: The ID of the comment for which you want to get reactions information.
        :param reaction_user_arn: Optional.
        :param next_token: An enumeration token that, when provided in a request, returns the next
        batch of the results.
        :param max_results: A non-zero, non-negative integer used to limit the number of returned
        results.
        :returns: GetCommentReactionsOutput
        :raises CommentDoesNotExistException:
        :raises CommentIdRequiredException:
        :raises InvalidCommentIdException:
        :raises InvalidReactionUserArnException:
        :raises InvalidMaxResultsException:
        :raises InvalidContinuationTokenException:
        :raises CommentDeletedException:
        """
        raise NotImplementedError

    @handler("GetCommentsForComparedCommit")
    def get_comments_for_compared_commit(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        after_commit_id: CommitId,
        before_commit_id: CommitId = None,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> GetCommentsForComparedCommitOutput:
        """Returns information about comments made on the comparison between two
        commits.

        Reaction counts might include numbers from user identities who were
        deleted after the reaction was made. For a count of reactions from
        active identities, use GetCommentReactions.

        :param repository_name: The name of the repository where you want to compare commits.
        :param after_commit_id: To establish the directionality of the comparison, the full commit ID of
        the after commit.
        :param before_commit_id: To establish the directionality of the comparison, the full commit ID of
        the before commit.
        :param next_token: An enumeration token that when provided in a request, returns the next
        batch of the results.
        :param max_results: A non-zero, non-negative integer used to limit the number of returned
        results.
        :returns: GetCommentsForComparedCommitOutput
        :raises RepositoryNameRequiredException:
        :raises RepositoryDoesNotExistException:
        :raises InvalidRepositoryNameException:
        :raises CommitIdRequiredException:
        :raises InvalidCommitIdException:
        :raises CommitDoesNotExistException:
        :raises InvalidMaxResultsException:
        :raises InvalidContinuationTokenException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("GetCommentsForPullRequest")
    def get_comments_for_pull_request(
        self,
        context: RequestContext,
        pull_request_id: PullRequestId,
        repository_name: RepositoryName = None,
        before_commit_id: CommitId = None,
        after_commit_id: CommitId = None,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> GetCommentsForPullRequestOutput:
        """Returns comments made on a pull request.

        Reaction counts might include numbers from user identities who were
        deleted after the reaction was made. For a count of reactions from
        active identities, use GetCommentReactions.

        :param pull_request_id: The system-generated ID of the pull request.
        :param repository_name: The name of the repository that contains the pull request.
        :param before_commit_id: The full commit ID of the commit in the destination branch that was the
        tip of the branch at the time the pull request was created.
        :param after_commit_id: The full commit ID of the commit in the source branch that was the tip
        of the branch at the time the comment was made.
        :param next_token: An enumeration token that, when provided in a request, returns the next
        batch of the results.
        :param max_results: A non-zero, non-negative integer used to limit the number of returned
        results.
        :returns: GetCommentsForPullRequestOutput
        :raises PullRequestIdRequiredException:
        :raises PullRequestDoesNotExistException:
        :raises InvalidPullRequestIdException:
        :raises RepositoryNameRequiredException:
        :raises RepositoryDoesNotExistException:
        :raises InvalidRepositoryNameException:
        :raises CommitIdRequiredException:
        :raises InvalidCommitIdException:
        :raises CommitDoesNotExistException:
        :raises InvalidMaxResultsException:
        :raises InvalidContinuationTokenException:
        :raises RepositoryNotAssociatedWithPullRequestException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("GetCommit")
    def get_commit(
        self, context: RequestContext, repository_name: RepositoryName, commit_id: ObjectId
    ) -> GetCommitOutput:
        """Returns information about a commit, including commit message and
        committer information.

        :param repository_name: The name of the repository to which the commit was made.
        :param commit_id: The commit ID.
        :returns: GetCommitOutput
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises CommitIdRequiredException:
        :raises InvalidCommitIdException:
        :raises CommitIdDoesNotExistException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("GetDifferences")
    def get_differences(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        after_commit_specifier: CommitName,
        before_commit_specifier: CommitName = None,
        before_path: Path = None,
        after_path: Path = None,
        max_results: Limit = None,
        next_token: NextToken = None,
    ) -> GetDifferencesOutput:
        """Returns information about the differences in a valid commit specifier
        (such as a branch, tag, HEAD, commit ID, or other fully qualified
        reference). Results can be limited to a specified path.

        :param repository_name: The name of the repository where you want to get differences.
        :param after_commit_specifier: The branch, tag, HEAD, or other fully qualified reference used to
        identify a commit.
        :param before_commit_specifier: The branch, tag, HEAD, or other fully qualified reference used to
        identify a commit (for example, the full commit ID).
        :param before_path: The file path in which to check for differences.
        :param after_path: The file path in which to check differences.
        :param max_results: A non-zero, non-negative integer used to limit the number of returned
        results.
        :param next_token: An enumeration token that, when provided in a request, returns the next
        batch of the results.
        :returns: GetDifferencesOutput
        :raises RepositoryNameRequiredException:
        :raises RepositoryDoesNotExistException:
        :raises InvalidRepositoryNameException:
        :raises InvalidContinuationTokenException:
        :raises InvalidMaxResultsException:
        :raises InvalidCommitIdException:
        :raises CommitRequiredException:
        :raises InvalidCommitException:
        :raises CommitDoesNotExistException:
        :raises InvalidPathException:
        :raises PathDoesNotExistException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("GetFile")
    def get_file(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        file_path: Path,
        commit_specifier: CommitName = None,
    ) -> GetFileOutput:
        """Returns the base-64 encoded contents of a specified file and its
        metadata.

        :param repository_name: The name of the repository that contains the file.
        :param file_path: The fully qualified path to the file, including the full name and
        extension of the file.
        :param commit_specifier: The fully quaified reference that identifies the commit that contains
        the file.
        :returns: GetFileOutput
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises InvalidCommitException:
        :raises CommitDoesNotExistException:
        :raises PathRequiredException:
        :raises InvalidPathException:
        :raises FileDoesNotExistException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        :raises FileTooLargeException:
        """
        raise NotImplementedError

    @handler("GetFolder")
    def get_folder(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        folder_path: Path,
        commit_specifier: CommitName = None,
    ) -> GetFolderOutput:
        """Returns the contents of a specified folder in a repository.

        :param repository_name: The name of the repository.
        :param folder_path: The fully qualified path to the folder whose contents are returned,
        including the folder name.
        :param commit_specifier: A fully qualified reference used to identify a commit that contains the
        version of the folder's content to return.
        :returns: GetFolderOutput
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises InvalidCommitException:
        :raises CommitDoesNotExistException:
        :raises PathRequiredException:
        :raises InvalidPathException:
        :raises FolderDoesNotExistException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("GetMergeCommit")
    def get_merge_commit(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        source_commit_specifier: CommitName,
        destination_commit_specifier: CommitName,
        conflict_detail_level: ConflictDetailLevelTypeEnum = None,
        conflict_resolution_strategy: ConflictResolutionStrategyTypeEnum = None,
    ) -> GetMergeCommitOutput:
        """Returns information about a specified merge commit.

        :param repository_name: The name of the repository that contains the merge commit about which
        you want to get information.
        :param source_commit_specifier: The branch, tag, HEAD, or other fully qualified reference used to
        identify a commit (for example, a branch name or a full commit ID).
        :param destination_commit_specifier: The branch, tag, HEAD, or other fully qualified reference used to
        identify a commit (for example, a branch name or a full commit ID).
        :param conflict_detail_level: The level of conflict detail to use.
        :param conflict_resolution_strategy: Specifies which branch to use when resolving conflicts, or whether to
        attempt automatically merging two versions of a file.
        :returns: GetMergeCommitOutput
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises CommitRequiredException:
        :raises InvalidCommitException:
        :raises CommitDoesNotExistException:
        :raises InvalidConflictDetailLevelException:
        :raises InvalidConflictResolutionStrategyException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("GetMergeConflicts")
    def get_merge_conflicts(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        destination_commit_specifier: CommitName,
        source_commit_specifier: CommitName,
        merge_option: MergeOptionTypeEnum,
        conflict_detail_level: ConflictDetailLevelTypeEnum = None,
        max_conflict_files: MaxResults = None,
        conflict_resolution_strategy: ConflictResolutionStrategyTypeEnum = None,
        next_token: NextToken = None,
    ) -> GetMergeConflictsOutput:
        """Returns information about merge conflicts between the before and after
        commit IDs for a pull request in a repository.

        :param repository_name: The name of the repository where the pull request was created.
        :param destination_commit_specifier: The branch, tag, HEAD, or other fully qualified reference used to
        identify a commit (for example, a branch name or a full commit ID).
        :param source_commit_specifier: The branch, tag, HEAD, or other fully qualified reference used to
        identify a commit (for example, a branch name or a full commit ID).
        :param merge_option: The merge option or strategy you want to use to merge the code.
        :param conflict_detail_level: The level of conflict detail to use.
        :param max_conflict_files: The maximum number of files to include in the output.
        :param conflict_resolution_strategy: Specifies which branch to use when resolving conflicts, or whether to
        attempt automatically merging two versions of a file.
        :param next_token: An enumeration token that, when provided in a request, returns the next
        batch of the results.
        :returns: GetMergeConflictsOutput
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises MergeOptionRequiredException:
        :raises InvalidMergeOptionException:
        :raises InvalidContinuationTokenException:
        :raises CommitRequiredException:
        :raises CommitDoesNotExistException:
        :raises InvalidCommitException:
        :raises TipsDivergenceExceededException:
        :raises InvalidMaxConflictFilesException:
        :raises InvalidConflictDetailLevelException:
        :raises InvalidDestinationCommitSpecifierException:
        :raises InvalidSourceCommitSpecifierException:
        :raises InvalidConflictResolutionStrategyException:
        :raises MaximumFileContentToLoadExceededException:
        :raises MaximumItemsToCompareExceededException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("GetMergeOptions")
    def get_merge_options(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        source_commit_specifier: CommitName,
        destination_commit_specifier: CommitName,
        conflict_detail_level: ConflictDetailLevelTypeEnum = None,
        conflict_resolution_strategy: ConflictResolutionStrategyTypeEnum = None,
    ) -> GetMergeOptionsOutput:
        """Returns information about the merge options available for merging two
        specified branches. For details about why a merge option is not
        available, use GetMergeConflicts or DescribeMergeConflicts.

        :param repository_name: The name of the repository that contains the commits about which you
        want to get merge options.
        :param source_commit_specifier: The branch, tag, HEAD, or other fully qualified reference used to
        identify a commit (for example, a branch name or a full commit ID).
        :param destination_commit_specifier: The branch, tag, HEAD, or other fully qualified reference used to
        identify a commit (for example, a branch name or a full commit ID).
        :param conflict_detail_level: The level of conflict detail to use.
        :param conflict_resolution_strategy: Specifies which branch to use when resolving conflicts, or whether to
        attempt automatically merging two versions of a file.
        :returns: GetMergeOptionsOutput
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises CommitRequiredException:
        :raises CommitDoesNotExistException:
        :raises InvalidCommitException:
        :raises TipsDivergenceExceededException:
        :raises InvalidConflictDetailLevelException:
        :raises InvalidConflictResolutionStrategyException:
        :raises MaximumFileContentToLoadExceededException:
        :raises MaximumItemsToCompareExceededException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("GetPullRequest")
    def get_pull_request(
        self, context: RequestContext, pull_request_id: PullRequestId
    ) -> GetPullRequestOutput:
        """Gets information about a pull request in a specified repository.

        :param pull_request_id: The system-generated ID of the pull request.
        :returns: GetPullRequestOutput
        :raises PullRequestDoesNotExistException:
        :raises InvalidPullRequestIdException:
        :raises PullRequestIdRequiredException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("GetPullRequestApprovalStates")
    def get_pull_request_approval_states(
        self, context: RequestContext, pull_request_id: PullRequestId, revision_id: RevisionId
    ) -> GetPullRequestApprovalStatesOutput:
        """Gets information about the approval states for a specified pull request.
        Approval states only apply to pull requests that have one or more
        approval rules applied to them.

        :param pull_request_id: The system-generated ID for the pull request.
        :param revision_id: The system-generated ID for the pull request revision.
        :returns: GetPullRequestApprovalStatesOutput
        :raises PullRequestDoesNotExistException:
        :raises InvalidPullRequestIdException:
        :raises PullRequestIdRequiredException:
        :raises InvalidRevisionIdException:
        :raises RevisionIdRequiredException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("GetPullRequestOverrideState")
    def get_pull_request_override_state(
        self, context: RequestContext, pull_request_id: PullRequestId, revision_id: RevisionId
    ) -> GetPullRequestOverrideStateOutput:
        """Returns information about whether approval rules have been set aside
        (overridden) for a pull request, and if so, the Amazon Resource Name
        (ARN) of the user or identity that overrode the rules and their
        requirements for the pull request.

        :param pull_request_id: The ID of the pull request for which you want to get information about
        whether approval rules have been set aside (overridden).
        :param revision_id: The system-generated ID of the revision for the pull request.
        :returns: GetPullRequestOverrideStateOutput
        :raises PullRequestDoesNotExistException:
        :raises InvalidPullRequestIdException:
        :raises PullRequestIdRequiredException:
        :raises InvalidRevisionIdException:
        :raises RevisionIdRequiredException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("GetRepository")
    def get_repository(
        self, context: RequestContext, repository_name: RepositoryName
    ) -> GetRepositoryOutput:
        """Returns information about a repository.

        The description field for a repository accepts all HTML characters and
        all valid Unicode characters. Applications that do not HTML-encode the
        description and display it in a webpage can expose users to potentially
        malicious code. Make sure that you HTML-encode the description field in
        any application that uses this API to display the repository description
        on a webpage.

        :param repository_name: The name of the repository to get information about.
        :returns: GetRepositoryOutput
        :raises RepositoryNameRequiredException:
        :raises RepositoryDoesNotExistException:
        :raises InvalidRepositoryNameException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("GetRepositoryTriggers")
    def get_repository_triggers(
        self, context: RequestContext, repository_name: RepositoryName
    ) -> GetRepositoryTriggersOutput:
        """Gets information about triggers configured for a repository.

        :param repository_name: The name of the repository for which the trigger is configured.
        :returns: GetRepositoryTriggersOutput
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("ListApprovalRuleTemplates")
    def list_approval_rule_templates(
        self, context: RequestContext, next_token: NextToken = None, max_results: MaxResults = None
    ) -> ListApprovalRuleTemplatesOutput:
        """Lists all approval rule templates in the specified AWS Region in your
        AWS account. If an AWS Region is not specified, the AWS Region where you
        are signed in is used.

        :param next_token: An enumeration token that, when provided in a request, returns the next
        batch of the results.
        :param max_results: A non-zero, non-negative integer used to limit the number of returned
        results.
        :returns: ListApprovalRuleTemplatesOutput
        :raises InvalidMaxResultsException:
        :raises InvalidContinuationTokenException:
        """
        raise NotImplementedError

    @handler("ListAssociatedApprovalRuleTemplatesForRepository")
    def list_associated_approval_rule_templates_for_repository(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListAssociatedApprovalRuleTemplatesForRepositoryOutput:
        """Lists all approval rule templates that are associated with a specified
        repository.

        :param repository_name: The name of the repository for which you want to list all associated
        approval rule templates.
        :param next_token: An enumeration token that, when provided in a request, returns the next
        batch of the results.
        :param max_results: A non-zero, non-negative integer used to limit the number of returned
        results.
        :returns: ListAssociatedApprovalRuleTemplatesForRepositoryOutput
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises InvalidMaxResultsException:
        :raises InvalidContinuationTokenException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("ListBranches")
    def list_branches(
        self, context: RequestContext, repository_name: RepositoryName, next_token: NextToken = None
    ) -> ListBranchesOutput:
        """Gets information about one or more branches in a repository.

        :param repository_name: The name of the repository that contains the branches.
        :param next_token: An enumeration token that allows the operation to batch the results.
        :returns: ListBranchesOutput
        :raises RepositoryNameRequiredException:
        :raises RepositoryDoesNotExistException:
        :raises InvalidRepositoryNameException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        :raises InvalidContinuationTokenException:
        """
        raise NotImplementedError

    @handler("ListPullRequests")
    def list_pull_requests(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        author_arn: Arn = None,
        pull_request_status: PullRequestStatusEnum = None,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListPullRequestsOutput:
        """Returns a list of pull requests for a specified repository. The return
        list can be refined by pull request status or pull request author ARN.

        :param repository_name: The name of the repository for which you want to list pull requests.
        :param author_arn: Optional.
        :param pull_request_status: Optional.
        :param next_token: An enumeration token that, when provided in a request, returns the next
        batch of the results.
        :param max_results: A non-zero, non-negative integer used to limit the number of returned
        results.
        :returns: ListPullRequestsOutput
        :raises InvalidPullRequestStatusException:
        :raises InvalidAuthorArnException:
        :raises AuthorDoesNotExistException:
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises InvalidMaxResultsException:
        :raises InvalidContinuationTokenException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("ListRepositories")
    def list_repositories(
        self,
        context: RequestContext,
        next_token: NextToken = None,
        sort_by: SortByEnum = None,
        order: OrderEnum = None,
    ) -> ListRepositoriesOutput:
        """Gets information about one or more repositories.

        :param next_token: An enumeration token that allows the operation to batch the results of
        the operation.
        :param sort_by: The criteria used to sort the results of a list repositories operation.
        :param order: The order in which to sort the results of a list repositories operation.
        :returns: ListRepositoriesOutput
        :raises InvalidSortByException:
        :raises InvalidOrderException:
        :raises InvalidContinuationTokenException:
        """
        raise NotImplementedError

    @handler("ListRepositoriesForApprovalRuleTemplate")
    def list_repositories_for_approval_rule_template(
        self,
        context: RequestContext,
        approval_rule_template_name: ApprovalRuleTemplateName,
        next_token: NextToken = None,
        max_results: MaxResults = None,
    ) -> ListRepositoriesForApprovalRuleTemplateOutput:
        """Lists all repositories associated with the specified approval rule
        template.

        :param approval_rule_template_name: The name of the approval rule template for which you want to list
        repositories that are associated with that template.
        :param next_token: An enumeration token that, when provided in a request, returns the next
        batch of the results.
        :param max_results: A non-zero, non-negative integer used to limit the number of returned
        results.
        :returns: ListRepositoriesForApprovalRuleTemplateOutput
        :raises ApprovalRuleTemplateNameRequiredException:
        :raises InvalidApprovalRuleTemplateNameException:
        :raises ApprovalRuleTemplateDoesNotExistException:
        :raises InvalidMaxResultsException:
        :raises InvalidContinuationTokenException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("ListTagsForResource")
    def list_tags_for_resource(
        self, context: RequestContext, resource_arn: ResourceArn, next_token: NextToken = None
    ) -> ListTagsForResourceOutput:
        """Gets information about AWS tags for a specified Amazon Resource Name
        (ARN) in AWS CodeCommit. For a list of valid resources in AWS
        CodeCommit, see `CodeCommit Resources and
        Operations <https://docs.aws.amazon.com/codecommit/latest/userguide/auth-and-access-control-iam-access-control-identity-based.html#arn-formats>`__
        in the *AWS CodeCommit User Guide*.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource for which you want to get
        information about tags, if any.
        :param next_token: An enumeration token that, when provided in a request, returns the next
        batch of the results.
        :returns: ListTagsForResourceOutput
        :raises RepositoryDoesNotExistException:
        :raises InvalidRepositoryNameException:
        :raises ResourceArnRequiredException:
        :raises InvalidResourceArnException:
        """
        raise NotImplementedError

    @handler("MergeBranchesByFastForward")
    def merge_branches_by_fast_forward(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        source_commit_specifier: CommitName,
        destination_commit_specifier: CommitName,
        target_branch: BranchName = None,
    ) -> MergeBranchesByFastForwardOutput:
        """Merges two branches using the fast-forward merge strategy.

        :param repository_name: The name of the repository where you want to merge two branches.
        :param source_commit_specifier: The branch, tag, HEAD, or other fully qualified reference used to
        identify a commit (for example, a branch name or a full commit ID).
        :param destination_commit_specifier: The branch, tag, HEAD, or other fully qualified reference used to
        identify a commit (for example, a branch name or a full commit ID).
        :param target_branch: The branch where the merge is applied.
        :returns: MergeBranchesByFastForwardOutput
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises TipsDivergenceExceededException:
        :raises CommitRequiredException:
        :raises InvalidCommitException:
        :raises CommitDoesNotExistException:
        :raises InvalidTargetBranchException:
        :raises InvalidBranchNameException:
        :raises BranchNameRequiredException:
        :raises BranchNameIsTagNameException:
        :raises BranchDoesNotExistException:
        :raises ManualMergeRequiredException:
        :raises ConcurrentReferenceUpdateException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("MergeBranchesBySquash")
    def merge_branches_by_squash(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        source_commit_specifier: CommitName,
        destination_commit_specifier: CommitName,
        target_branch: BranchName = None,
        conflict_detail_level: ConflictDetailLevelTypeEnum = None,
        conflict_resolution_strategy: ConflictResolutionStrategyTypeEnum = None,
        author_name: Name = None,
        email: Email = None,
        commit_message: Message = None,
        keep_empty_folders: KeepEmptyFolders = None,
        conflict_resolution: ConflictResolution = None,
    ) -> MergeBranchesBySquashOutput:
        """Merges two branches using the squash merge strategy.

        :param repository_name: The name of the repository where you want to merge two branches.
        :param source_commit_specifier: The branch, tag, HEAD, or other fully qualified reference used to
        identify a commit (for example, a branch name or a full commit ID).
        :param destination_commit_specifier: The branch, tag, HEAD, or other fully qualified reference used to
        identify a commit (for example, a branch name or a full commit ID).
        :param target_branch: The branch where the merge is applied.
        :param conflict_detail_level: The level of conflict detail to use.
        :param conflict_resolution_strategy: Specifies which branch to use when resolving conflicts, or whether to
        attempt automatically merging two versions of a file.
        :param author_name: The name of the author who created the commit.
        :param email: The email address of the person merging the branches.
        :param commit_message: The commit message for the merge.
        :param keep_empty_folders: If the commit contains deletions, whether to keep a folder or folder
        structure if the changes leave the folders empty.
        :param conflict_resolution: If AUTOMERGE is the conflict resolution strategy, a list of inputs to
        use when resolving conflicts during a merge.
        :returns: MergeBranchesBySquashOutput
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises TipsDivergenceExceededException:
        :raises CommitRequiredException:
        :raises InvalidCommitException:
        :raises CommitDoesNotExistException:
        :raises InvalidTargetBranchException:
        :raises InvalidBranchNameException:
        :raises BranchNameRequiredException:
        :raises BranchNameIsTagNameException:
        :raises BranchDoesNotExistException:
        :raises ManualMergeRequiredException:
        :raises InvalidConflictDetailLevelException:
        :raises InvalidConflictResolutionStrategyException:
        :raises InvalidConflictResolutionException:
        :raises MaximumConflictResolutionEntriesExceededException:
        :raises MultipleConflictResolutionEntriesException:
        :raises ReplacementTypeRequiredException:
        :raises InvalidReplacementTypeException:
        :raises ReplacementContentRequiredException:
        :raises InvalidReplacementContentException:
        :raises PathRequiredException:
        :raises InvalidPathException:
        :raises FileContentSizeLimitExceededException:
        :raises FolderContentSizeLimitExceededException:
        :raises MaximumFileContentToLoadExceededException:
        :raises MaximumItemsToCompareExceededException:
        :raises FileModeRequiredException:
        :raises InvalidFileModeException:
        :raises NameLengthExceededException:
        :raises InvalidEmailException:
        :raises CommitMessageLengthExceededException:
        :raises ConcurrentReferenceUpdateException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("MergeBranchesByThreeWay")
    def merge_branches_by_three_way(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        source_commit_specifier: CommitName,
        destination_commit_specifier: CommitName,
        target_branch: BranchName = None,
        conflict_detail_level: ConflictDetailLevelTypeEnum = None,
        conflict_resolution_strategy: ConflictResolutionStrategyTypeEnum = None,
        author_name: Name = None,
        email: Email = None,
        commit_message: Message = None,
        keep_empty_folders: KeepEmptyFolders = None,
        conflict_resolution: ConflictResolution = None,
    ) -> MergeBranchesByThreeWayOutput:
        """Merges two specified branches using the three-way merge strategy.

        :param repository_name: The name of the repository where you want to merge two branches.
        :param source_commit_specifier: The branch, tag, HEAD, or other fully qualified reference used to
        identify a commit (for example, a branch name or a full commit ID).
        :param destination_commit_specifier: The branch, tag, HEAD, or other fully qualified reference used to
        identify a commit (for example, a branch name or a full commit ID).
        :param target_branch: The branch where the merge is applied.
        :param conflict_detail_level: The level of conflict detail to use.
        :param conflict_resolution_strategy: Specifies which branch to use when resolving conflicts, or whether to
        attempt automatically merging two versions of a file.
        :param author_name: The name of the author who created the commit.
        :param email: The email address of the person merging the branches.
        :param commit_message: The commit message to include in the commit information for the merge.
        :param keep_empty_folders: If the commit contains deletions, whether to keep a folder or folder
        structure if the changes leave the folders empty.
        :param conflict_resolution: If AUTOMERGE is the conflict resolution strategy, a list of inputs to
        use when resolving conflicts during a merge.
        :returns: MergeBranchesByThreeWayOutput
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises TipsDivergenceExceededException:
        :raises CommitRequiredException:
        :raises InvalidCommitException:
        :raises CommitDoesNotExistException:
        :raises InvalidTargetBranchException:
        :raises InvalidBranchNameException:
        :raises BranchNameRequiredException:
        :raises BranchNameIsTagNameException:
        :raises BranchDoesNotExistException:
        :raises ManualMergeRequiredException:
        :raises ConcurrentReferenceUpdateException:
        :raises InvalidConflictDetailLevelException:
        :raises InvalidConflictResolutionStrategyException:
        :raises InvalidConflictResolutionException:
        :raises MaximumConflictResolutionEntriesExceededException:
        :raises MultipleConflictResolutionEntriesException:
        :raises ReplacementTypeRequiredException:
        :raises InvalidReplacementTypeException:
        :raises ReplacementContentRequiredException:
        :raises InvalidReplacementContentException:
        :raises PathRequiredException:
        :raises InvalidPathException:
        :raises FileContentSizeLimitExceededException:
        :raises FolderContentSizeLimitExceededException:
        :raises MaximumFileContentToLoadExceededException:
        :raises MaximumItemsToCompareExceededException:
        :raises FileModeRequiredException:
        :raises InvalidFileModeException:
        :raises NameLengthExceededException:
        :raises InvalidEmailException:
        :raises CommitMessageLengthExceededException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("MergePullRequestByFastForward")
    def merge_pull_request_by_fast_forward(
        self,
        context: RequestContext,
        pull_request_id: PullRequestId,
        repository_name: RepositoryName,
        source_commit_id: ObjectId = None,
    ) -> MergePullRequestByFastForwardOutput:
        """Attempts to merge the source commit of a pull request into the specified
        destination branch for that pull request at the specified commit using
        the fast-forward merge strategy. If the merge is successful, it closes
        the pull request.

        :param pull_request_id: The system-generated ID of the pull request.
        :param repository_name: The name of the repository where the pull request was created.
        :param source_commit_id: The full commit ID of the original or updated commit in the pull request
        source branch.
        :returns: MergePullRequestByFastForwardOutput
        :raises ManualMergeRequiredException:
        :raises PullRequestAlreadyClosedException:
        :raises PullRequestDoesNotExistException:
        :raises InvalidPullRequestIdException:
        :raises PullRequestIdRequiredException:
        :raises TipOfSourceReferenceIsDifferentException:
        :raises ReferenceDoesNotExistException:
        :raises InvalidCommitIdException:
        :raises RepositoryNotAssociatedWithPullRequestException:
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises ConcurrentReferenceUpdateException:
        :raises PullRequestApprovalRulesNotSatisfiedException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("MergePullRequestBySquash")
    def merge_pull_request_by_squash(
        self,
        context: RequestContext,
        pull_request_id: PullRequestId,
        repository_name: RepositoryName,
        source_commit_id: ObjectId = None,
        conflict_detail_level: ConflictDetailLevelTypeEnum = None,
        conflict_resolution_strategy: ConflictResolutionStrategyTypeEnum = None,
        commit_message: Message = None,
        author_name: Name = None,
        email: Email = None,
        keep_empty_folders: KeepEmptyFolders = None,
        conflict_resolution: ConflictResolution = None,
    ) -> MergePullRequestBySquashOutput:
        """Attempts to merge the source commit of a pull request into the specified
        destination branch for that pull request at the specified commit using
        the squash merge strategy. If the merge is successful, it closes the
        pull request.

        :param pull_request_id: The system-generated ID of the pull request.
        :param repository_name: The name of the repository where the pull request was created.
        :param source_commit_id: The full commit ID of the original or updated commit in the pull request
        source branch.
        :param conflict_detail_level: The level of conflict detail to use.
        :param conflict_resolution_strategy: Specifies which branch to use when resolving conflicts, or whether to
        attempt automatically merging two versions of a file.
        :param commit_message: The commit message to include in the commit information for the merge.
        :param author_name: The name of the author who created the commit.
        :param email: The email address of the person merging the branches.
        :param keep_empty_folders: If the commit contains deletions, whether to keep a folder or folder
        structure if the changes leave the folders empty.
        :param conflict_resolution: If AUTOMERGE is the conflict resolution strategy, a list of inputs to
        use when resolving conflicts during a merge.
        :returns: MergePullRequestBySquashOutput
        :raises PullRequestAlreadyClosedException:
        :raises PullRequestDoesNotExistException:
        :raises PullRequestIdRequiredException:
        :raises InvalidPullRequestIdException:
        :raises InvalidCommitIdException:
        :raises ManualMergeRequiredException:
        :raises TipOfSourceReferenceIsDifferentException:
        :raises TipsDivergenceExceededException:
        :raises NameLengthExceededException:
        :raises InvalidEmailException:
        :raises CommitMessageLengthExceededException:
        :raises InvalidConflictDetailLevelException:
        :raises InvalidConflictResolutionStrategyException:
        :raises InvalidConflictResolutionException:
        :raises ReplacementTypeRequiredException:
        :raises InvalidReplacementTypeException:
        :raises MultipleConflictResolutionEntriesException:
        :raises ReplacementContentRequiredException:
        :raises MaximumConflictResolutionEntriesExceededException:
        :raises ConcurrentReferenceUpdateException:
        :raises PathRequiredException:
        :raises InvalidPathException:
        :raises InvalidFileModeException:
        :raises InvalidReplacementContentException:
        :raises FileContentSizeLimitExceededException:
        :raises FolderContentSizeLimitExceededException:
        :raises MaximumFileContentToLoadExceededException:
        :raises MaximumItemsToCompareExceededException:
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises RepositoryNotAssociatedWithPullRequestException:
        :raises PullRequestApprovalRulesNotSatisfiedException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("MergePullRequestByThreeWay")
    def merge_pull_request_by_three_way(
        self,
        context: RequestContext,
        pull_request_id: PullRequestId,
        repository_name: RepositoryName,
        source_commit_id: ObjectId = None,
        conflict_detail_level: ConflictDetailLevelTypeEnum = None,
        conflict_resolution_strategy: ConflictResolutionStrategyTypeEnum = None,
        commit_message: Message = None,
        author_name: Name = None,
        email: Email = None,
        keep_empty_folders: KeepEmptyFolders = None,
        conflict_resolution: ConflictResolution = None,
    ) -> MergePullRequestByThreeWayOutput:
        """Attempts to merge the source commit of a pull request into the specified
        destination branch for that pull request at the specified commit using
        the three-way merge strategy. If the merge is successful, it closes the
        pull request.

        :param pull_request_id: The system-generated ID of the pull request.
        :param repository_name: The name of the repository where the pull request was created.
        :param source_commit_id: The full commit ID of the original or updated commit in the pull request
        source branch.
        :param conflict_detail_level: The level of conflict detail to use.
        :param conflict_resolution_strategy: Specifies which branch to use when resolving conflicts, or whether to
        attempt automatically merging two versions of a file.
        :param commit_message: The commit message to include in the commit information for the merge.
        :param author_name: The name of the author who created the commit.
        :param email: The email address of the person merging the branches.
        :param keep_empty_folders: If the commit contains deletions, whether to keep a folder or folder
        structure if the changes leave the folders empty.
        :param conflict_resolution: If AUTOMERGE is the conflict resolution strategy, a list of inputs to
        use when resolving conflicts during a merge.
        :returns: MergePullRequestByThreeWayOutput
        :raises PullRequestAlreadyClosedException:
        :raises PullRequestDoesNotExistException:
        :raises PullRequestIdRequiredException:
        :raises InvalidPullRequestIdException:
        :raises InvalidCommitIdException:
        :raises ManualMergeRequiredException:
        :raises TipOfSourceReferenceIsDifferentException:
        :raises TipsDivergenceExceededException:
        :raises NameLengthExceededException:
        :raises InvalidEmailException:
        :raises CommitMessageLengthExceededException:
        :raises InvalidConflictDetailLevelException:
        :raises InvalidConflictResolutionStrategyException:
        :raises InvalidConflictResolutionException:
        :raises ReplacementTypeRequiredException:
        :raises InvalidReplacementTypeException:
        :raises MultipleConflictResolutionEntriesException:
        :raises ReplacementContentRequiredException:
        :raises MaximumConflictResolutionEntriesExceededException:
        :raises PathRequiredException:
        :raises InvalidPathException:
        :raises InvalidFileModeException:
        :raises InvalidReplacementContentException:
        :raises FileContentSizeLimitExceededException:
        :raises FolderContentSizeLimitExceededException:
        :raises MaximumFileContentToLoadExceededException:
        :raises MaximumItemsToCompareExceededException:
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises RepositoryNotAssociatedWithPullRequestException:
        :raises ConcurrentReferenceUpdateException:
        :raises PullRequestApprovalRulesNotSatisfiedException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("OverridePullRequestApprovalRules")
    def override_pull_request_approval_rules(
        self,
        context: RequestContext,
        pull_request_id: PullRequestId,
        revision_id: RevisionId,
        override_status: OverrideStatus,
    ) -> None:
        """Sets aside (overrides) all approval rule requirements for a specified
        pull request.

        :param pull_request_id: The system-generated ID of the pull request for which you want to
        override all approval rule requirements.
        :param revision_id: The system-generated ID of the most recent revision of the pull request.
        :param override_status: Whether you want to set aside approval rule requirements for the pull
        request (OVERRIDE) or revoke a previous override and apply approval rule
        requirements (REVOKE).
        :raises PullRequestDoesNotExistException:
        :raises InvalidPullRequestIdException:
        :raises PullRequestIdRequiredException:
        :raises InvalidRevisionIdException:
        :raises RevisionIdRequiredException:
        :raises InvalidOverrideStatusException:
        :raises OverrideStatusRequiredException:
        :raises OverrideAlreadySetException:
        :raises RevisionNotCurrentException:
        :raises PullRequestAlreadyClosedException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("PostCommentForComparedCommit")
    def post_comment_for_compared_commit(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        after_commit_id: CommitId,
        content: Content,
        before_commit_id: CommitId = None,
        location: Location = None,
        client_request_token: ClientRequestToken = None,
    ) -> PostCommentForComparedCommitOutput:
        """Posts a comment on the comparison between two commits.

        :param repository_name: The name of the repository where you want to post a comment on the
        comparison between commits.
        :param after_commit_id: To establish the directionality of the comparison, the full commit ID of
        the after commit.
        :param content: The content of the comment you want to make.
        :param before_commit_id: To establish the directionality of the comparison, the full commit ID of
        the before commit.
        :param location: The location of the comparison where you want to comment.
        :param client_request_token: A unique, client-generated idempotency token that, when provided in a
        request, ensures the request cannot be repeated with a changed
        parameter.
        :returns: PostCommentForComparedCommitOutput
        :raises RepositoryNameRequiredException:
        :raises RepositoryDoesNotExistException:
        :raises InvalidRepositoryNameException:
        :raises ClientRequestTokenRequiredException:
        :raises InvalidClientRequestTokenException:
        :raises IdempotencyParameterMismatchException:
        :raises CommentContentRequiredException:
        :raises CommentContentSizeLimitExceededException:
        :raises InvalidFileLocationException:
        :raises InvalidRelativeFileVersionEnumException:
        :raises PathRequiredException:
        :raises InvalidFilePositionException:
        :raises CommitIdRequiredException:
        :raises InvalidCommitIdException:
        :raises BeforeCommitIdAndAfterCommitIdAreSameException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        :raises CommitDoesNotExistException:
        :raises InvalidPathException:
        :raises PathDoesNotExistException:
        :raises PathRequiredException:
        """
        raise NotImplementedError

    @handler("PostCommentForPullRequest")
    def post_comment_for_pull_request(
        self,
        context: RequestContext,
        pull_request_id: PullRequestId,
        repository_name: RepositoryName,
        before_commit_id: CommitId,
        after_commit_id: CommitId,
        content: Content,
        location: Location = None,
        client_request_token: ClientRequestToken = None,
    ) -> PostCommentForPullRequestOutput:
        """Posts a comment on a pull request.

        :param pull_request_id: The system-generated ID of the pull request.
        :param repository_name: The name of the repository where you want to post a comment on a pull
        request.
        :param before_commit_id: The full commit ID of the commit in the destination branch that was the
        tip of the branch at the time the pull request was created.
        :param after_commit_id: The full commit ID of the commit in the source branch that is the
        current tip of the branch for the pull request when you post the
        comment.
        :param content: The content of your comment on the change.
        :param location: The location of the change where you want to post your comment.
        :param client_request_token: A unique, client-generated idempotency token that, when provided in a
        request, ensures the request cannot be repeated with a changed
        parameter.
        :returns: PostCommentForPullRequestOutput
        :raises PullRequestDoesNotExistException:
        :raises InvalidPullRequestIdException:
        :raises PullRequestIdRequiredException:
        :raises RepositoryNotAssociatedWithPullRequestException:
        :raises RepositoryNameRequiredException:
        :raises RepositoryDoesNotExistException:
        :raises InvalidRepositoryNameException:
        :raises ClientRequestTokenRequiredException:
        :raises InvalidClientRequestTokenException:
        :raises IdempotencyParameterMismatchException:
        :raises CommentContentRequiredException:
        :raises CommentContentSizeLimitExceededException:
        :raises InvalidFileLocationException:
        :raises InvalidRelativeFileVersionEnumException:
        :raises PathRequiredException:
        :raises InvalidFilePositionException:
        :raises CommitIdRequiredException:
        :raises InvalidCommitIdException:
        :raises BeforeCommitIdAndAfterCommitIdAreSameException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        :raises CommitDoesNotExistException:
        :raises InvalidPathException:
        :raises PathDoesNotExistException:
        :raises PathRequiredException:
        """
        raise NotImplementedError

    @handler("PostCommentReply")
    def post_comment_reply(
        self,
        context: RequestContext,
        in_reply_to: CommentId,
        content: Content,
        client_request_token: ClientRequestToken = None,
    ) -> PostCommentReplyOutput:
        """Posts a comment in reply to an existing comment on a comparison between
        commits or a pull request.

        :param in_reply_to: The system-generated ID of the comment to which you want to reply.
        :param content: The contents of your reply to a comment.
        :param client_request_token: A unique, client-generated idempotency token that, when provided in a
        request, ensures the request cannot be repeated with a changed
        parameter.
        :returns: PostCommentReplyOutput
        :raises ClientRequestTokenRequiredException:
        :raises InvalidClientRequestTokenException:
        :raises IdempotencyParameterMismatchException:
        :raises CommentContentRequiredException:
        :raises CommentContentSizeLimitExceededException:
        :raises CommentDoesNotExistException:
        :raises CommentIdRequiredException:
        :raises InvalidCommentIdException:
        """
        raise NotImplementedError

    @handler("PutCommentReaction")
    def put_comment_reaction(
        self, context: RequestContext, comment_id: CommentId, reaction_value: ReactionValue
    ) -> None:
        """Adds or updates a reaction to a specified comment for the user whose
        identity is used to make the request. You can only add or update a
        reaction for yourself. You cannot add, modify, or delete a reaction for
        another user.

        :param comment_id: The ID of the comment to which you want to add or update a reaction.
        :param reaction_value: The emoji reaction you want to add or update.
        :raises CommentDoesNotExistException:
        :raises CommentIdRequiredException:
        :raises InvalidCommentIdException:
        :raises InvalidReactionValueException:
        :raises ReactionValueRequiredException:
        :raises ReactionLimitExceededException:
        :raises CommentDeletedException:
        """
        raise NotImplementedError

    @handler("PutFile")
    def put_file(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        branch_name: BranchName,
        file_content: FileContent,
        file_path: Path,
        file_mode: FileModeTypeEnum = None,
        parent_commit_id: CommitId = None,
        commit_message: Message = None,
        name: Name = None,
        email: Email = None,
    ) -> PutFileOutput:
        """Adds or updates a file in a branch in an AWS CodeCommit repository, and
        generates a commit for the addition in the specified branch.

        :param repository_name: The name of the repository where you want to add or update the file.
        :param branch_name: The name of the branch where you want to add or update the file.
        :param file_content: The content of the file, in binary object format.
        :param file_path: The name of the file you want to add or update, including the relative
        path to the file in the repository.
        :param file_mode: The file mode permissions of the blob.
        :param parent_commit_id: The full commit ID of the head commit in the branch where you want to
        add or update the file.
        :param commit_message: A message about why this file was added or updated.
        :param name: The name of the person adding or updating the file.
        :param email: An email address for the person adding or updating the file.
        :returns: PutFileOutput
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryDoesNotExistException:
        :raises ParentCommitIdRequiredException:
        :raises InvalidParentCommitIdException:
        :raises ParentCommitDoesNotExistException:
        :raises ParentCommitIdOutdatedException:
        :raises FileContentRequiredException:
        :raises FileContentSizeLimitExceededException:
        :raises FolderContentSizeLimitExceededException:
        :raises PathRequiredException:
        :raises InvalidPathException:
        :raises BranchNameRequiredException:
        :raises InvalidBranchNameException:
        :raises BranchDoesNotExistException:
        :raises BranchNameIsTagNameException:
        :raises InvalidFileModeException:
        :raises NameLengthExceededException:
        :raises InvalidEmailException:
        :raises CommitMessageLengthExceededException:
        :raises InvalidDeletionParameterException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        :raises SameFileContentException:
        :raises FileNameConflictsWithDirectoryNameException:
        :raises DirectoryNameConflictsWithFileNameException:
        :raises FilePathConflictsWithSubmodulePathException:
        """
        raise NotImplementedError

    @handler("PutRepositoryTriggers")
    def put_repository_triggers(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        triggers: RepositoryTriggersList,
    ) -> PutRepositoryTriggersOutput:
        """Replaces all triggers for a repository. Used to create or delete
        triggers.

        :param repository_name: The name of the repository where you want to create or update the
        trigger.
        :param triggers: The JSON block of configuration information for each trigger.
        :returns: PutRepositoryTriggersOutput
        :raises RepositoryDoesNotExistException:
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryTriggersListRequiredException:
        :raises MaximumRepositoryTriggersExceededException:
        :raises InvalidRepositoryTriggerNameException:
        :raises InvalidRepositoryTriggerDestinationArnException:
        :raises InvalidRepositoryTriggerRegionException:
        :raises InvalidRepositoryTriggerCustomDataException:
        :raises MaximumBranchesExceededException:
        :raises InvalidRepositoryTriggerBranchNameException:
        :raises InvalidRepositoryTriggerEventsException:
        :raises RepositoryTriggerNameRequiredException:
        :raises RepositoryTriggerDestinationArnRequiredException:
        :raises RepositoryTriggerBranchNameListRequiredException:
        :raises RepositoryTriggerEventsListRequiredException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("TagResource")
    def tag_resource(
        self, context: RequestContext, resource_arn: ResourceArn, tags: TagsMap
    ) -> None:
        """Adds or updates tags for a resource in AWS CodeCommit. For a list of
        valid resources in AWS CodeCommit, see `CodeCommit Resources and
        Operations <https://docs.aws.amazon.com/codecommit/latest/userguide/auth-and-access-control-iam-access-control-identity-based.html#arn-formats>`__
        in the *AWS CodeCommit User Guide*.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource to which you want to add
        or update tags.
        :param tags: The key-value pair to use when tagging this repository.
        :raises RepositoryDoesNotExistException:
        :raises InvalidRepositoryNameException:
        :raises ResourceArnRequiredException:
        :raises InvalidResourceArnException:
        :raises TagsMapRequiredException:
        :raises InvalidTagsMapException:
        :raises TooManyTagsException:
        :raises InvalidSystemTagUsageException:
        :raises TagPolicyException:
        """
        raise NotImplementedError

    @handler("TestRepositoryTriggers")
    def test_repository_triggers(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        triggers: RepositoryTriggersList,
    ) -> TestRepositoryTriggersOutput:
        """Tests the functionality of repository triggers by sending information to
        the trigger target. If real data is available in the repository, the
        test sends data from the last commit. If no data is available, sample
        data is generated.

        :param repository_name: The name of the repository in which to test the triggers.
        :param triggers: The list of triggers to test.
        :returns: TestRepositoryTriggersOutput
        :raises RepositoryDoesNotExistException:
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        :raises RepositoryTriggersListRequiredException:
        :raises MaximumRepositoryTriggersExceededException:
        :raises InvalidRepositoryTriggerNameException:
        :raises InvalidRepositoryTriggerDestinationArnException:
        :raises InvalidRepositoryTriggerRegionException:
        :raises InvalidRepositoryTriggerCustomDataException:
        :raises MaximumBranchesExceededException:
        :raises InvalidRepositoryTriggerBranchNameException:
        :raises InvalidRepositoryTriggerEventsException:
        :raises RepositoryTriggerNameRequiredException:
        :raises RepositoryTriggerDestinationArnRequiredException:
        :raises RepositoryTriggerBranchNameListRequiredException:
        :raises RepositoryTriggerEventsListRequiredException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("UntagResource")
    def untag_resource(
        self, context: RequestContext, resource_arn: ResourceArn, tag_keys: TagKeysList
    ) -> None:
        """Removes tags for a resource in AWS CodeCommit. For a list of valid
        resources in AWS CodeCommit, see `CodeCommit Resources and
        Operations <https://docs.aws.amazon.com/codecommit/latest/userguide/auth-and-access-control-iam-access-control-identity-based.html#arn-formats>`__
        in the *AWS CodeCommit User Guide*.

        :param resource_arn: The Amazon Resource Name (ARN) of the resource to which you want to
        remove tags.
        :param tag_keys: The tag key for each tag that you want to remove from the resource.
        :raises RepositoryDoesNotExistException:
        :raises InvalidRepositoryNameException:
        :raises ResourceArnRequiredException:
        :raises InvalidResourceArnException:
        :raises TagKeysListRequiredException:
        :raises InvalidTagKeysListException:
        :raises TooManyTagsException:
        :raises InvalidSystemTagUsageException:
        :raises TagPolicyException:
        """
        raise NotImplementedError

    @handler("UpdateApprovalRuleTemplateContent")
    def update_approval_rule_template_content(
        self,
        context: RequestContext,
        approval_rule_template_name: ApprovalRuleTemplateName,
        new_rule_content: ApprovalRuleTemplateContent,
        existing_rule_content_sha256: RuleContentSha256 = None,
    ) -> UpdateApprovalRuleTemplateContentOutput:
        """Updates the content of an approval rule template. You can change the
        number of required approvals, the membership of the approval rule, and
        whether an approval pool is defined.

        :param approval_rule_template_name: The name of the approval rule template where you want to update the
        content of the rule.
        :param new_rule_content: The content that replaces the existing content of the rule.
        :param existing_rule_content_sha256: The SHA-256 hash signature for the content of the approval rule.
        :returns: UpdateApprovalRuleTemplateContentOutput
        :raises InvalidApprovalRuleTemplateNameException:
        :raises ApprovalRuleTemplateNameRequiredException:
        :raises ApprovalRuleTemplateDoesNotExistException:
        :raises InvalidApprovalRuleTemplateContentException:
        :raises InvalidRuleContentSha256Exception:
        :raises ApprovalRuleTemplateContentRequiredException:
        """
        raise NotImplementedError

    @handler("UpdateApprovalRuleTemplateDescription")
    def update_approval_rule_template_description(
        self,
        context: RequestContext,
        approval_rule_template_name: ApprovalRuleTemplateName,
        approval_rule_template_description: ApprovalRuleTemplateDescription,
    ) -> UpdateApprovalRuleTemplateDescriptionOutput:
        """Updates the description for a specified approval rule template.

        :param approval_rule_template_name: The name of the template for which you want to update the description.
        :param approval_rule_template_description: The updated description of the approval rule template.
        :returns: UpdateApprovalRuleTemplateDescriptionOutput
        :raises InvalidApprovalRuleTemplateNameException:
        :raises ApprovalRuleTemplateNameRequiredException:
        :raises ApprovalRuleTemplateDoesNotExistException:
        :raises InvalidApprovalRuleTemplateDescriptionException:
        """
        raise NotImplementedError

    @handler("UpdateApprovalRuleTemplateName")
    def update_approval_rule_template_name(
        self,
        context: RequestContext,
        old_approval_rule_template_name: ApprovalRuleTemplateName,
        new_approval_rule_template_name: ApprovalRuleTemplateName,
    ) -> UpdateApprovalRuleTemplateNameOutput:
        """Updates the name of a specified approval rule template.

        :param old_approval_rule_template_name: The current name of the approval rule template.
        :param new_approval_rule_template_name: The new name you want to apply to the approval rule template.
        :returns: UpdateApprovalRuleTemplateNameOutput
        :raises InvalidApprovalRuleTemplateNameException:
        :raises ApprovalRuleTemplateNameRequiredException:
        :raises ApprovalRuleTemplateDoesNotExistException:
        :raises ApprovalRuleTemplateNameAlreadyExistsException:
        """
        raise NotImplementedError

    @handler("UpdateComment")
    def update_comment(
        self, context: RequestContext, comment_id: CommentId, content: Content
    ) -> UpdateCommentOutput:
        """Replaces the contents of a comment.

        :param comment_id: The system-generated ID of the comment you want to update.
        :param content: The updated content to replace the existing content of the comment.
        :returns: UpdateCommentOutput
        :raises CommentContentRequiredException:
        :raises CommentContentSizeLimitExceededException:
        :raises CommentDoesNotExistException:
        :raises CommentIdRequiredException:
        :raises InvalidCommentIdException:
        :raises CommentNotCreatedByCallerException:
        :raises CommentDeletedException:
        """
        raise NotImplementedError

    @handler("UpdateDefaultBranch")
    def update_default_branch(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        default_branch_name: BranchName,
    ) -> None:
        """Sets or changes the default branch name for the specified repository.

        If you use this operation to change the default branch name to the
        current default branch name, a success message is returned even though
        the default branch did not change.

        :param repository_name: The name of the repository to set or change the default branch for.
        :param default_branch_name: The name of the branch to set as the default.
        :raises RepositoryNameRequiredException:
        :raises RepositoryDoesNotExistException:
        :raises InvalidRepositoryNameException:
        :raises BranchNameRequiredException:
        :raises InvalidBranchNameException:
        :raises BranchDoesNotExistException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("UpdatePullRequestApprovalRuleContent")
    def update_pull_request_approval_rule_content(
        self,
        context: RequestContext,
        pull_request_id: PullRequestId,
        approval_rule_name: ApprovalRuleName,
        new_rule_content: ApprovalRuleContent,
        existing_rule_content_sha256: RuleContentSha256 = None,
    ) -> UpdatePullRequestApprovalRuleContentOutput:
        """Updates the structure of an approval rule created specifically for a
        pull request. For example, you can change the number of required
        approvers and the approval pool for approvers.

        :param pull_request_id: The system-generated ID of the pull request.
        :param approval_rule_name: The name of the approval rule you want to update.
        :param new_rule_content: The updated content for the approval rule.
        :param existing_rule_content_sha256: The SHA-256 hash signature for the content of the approval rule.
        :returns: UpdatePullRequestApprovalRuleContentOutput
        :raises PullRequestDoesNotExistException:
        :raises InvalidPullRequestIdException:
        :raises PullRequestIdRequiredException:
        :raises PullRequestAlreadyClosedException:
        :raises ApprovalRuleNameRequiredException:
        :raises InvalidApprovalRuleNameException:
        :raises ApprovalRuleDoesNotExistException:
        :raises InvalidRuleContentSha256Exception:
        :raises ApprovalRuleContentRequiredException:
        :raises InvalidApprovalRuleContentException:
        :raises CannotModifyApprovalRuleFromTemplateException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("UpdatePullRequestApprovalState")
    def update_pull_request_approval_state(
        self,
        context: RequestContext,
        pull_request_id: PullRequestId,
        revision_id: RevisionId,
        approval_state: ApprovalState,
    ) -> None:
        """Updates the state of a user's approval on a pull request. The user is
        derived from the signed-in account when the request is made.

        :param pull_request_id: The system-generated ID of the pull request.
        :param revision_id: The system-generated ID of the revision.
        :param approval_state: The approval state to associate with the user on the pull request.
        :raises PullRequestDoesNotExistException:
        :raises InvalidPullRequestIdException:
        :raises PullRequestIdRequiredException:
        :raises InvalidRevisionIdException:
        :raises RevisionIdRequiredException:
        :raises InvalidApprovalStateException:
        :raises ApprovalStateRequiredException:
        :raises PullRequestCannotBeApprovedByAuthorException:
        :raises RevisionNotCurrentException:
        :raises PullRequestAlreadyClosedException:
        :raises MaximumNumberOfApprovalsExceededException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("UpdatePullRequestDescription")
    def update_pull_request_description(
        self, context: RequestContext, pull_request_id: PullRequestId, description: Description
    ) -> UpdatePullRequestDescriptionOutput:
        """Replaces the contents of the description of a pull request.

        :param pull_request_id: The system-generated ID of the pull request.
        :param description: The updated content of the description for the pull request.
        :returns: UpdatePullRequestDescriptionOutput
        :raises PullRequestDoesNotExistException:
        :raises InvalidPullRequestIdException:
        :raises PullRequestIdRequiredException:
        :raises InvalidDescriptionException:
        :raises PullRequestAlreadyClosedException:
        """
        raise NotImplementedError

    @handler("UpdatePullRequestStatus")
    def update_pull_request_status(
        self,
        context: RequestContext,
        pull_request_id: PullRequestId,
        pull_request_status: PullRequestStatusEnum,
    ) -> UpdatePullRequestStatusOutput:
        """Updates the status of a pull request.

        :param pull_request_id: The system-generated ID of the pull request.
        :param pull_request_status: The status of the pull request.
        :returns: UpdatePullRequestStatusOutput
        :raises PullRequestDoesNotExistException:
        :raises InvalidPullRequestIdException:
        :raises PullRequestIdRequiredException:
        :raises InvalidPullRequestStatusUpdateException:
        :raises InvalidPullRequestStatusException:
        :raises PullRequestStatusRequiredException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("UpdatePullRequestTitle")
    def update_pull_request_title(
        self, context: RequestContext, pull_request_id: PullRequestId, title: Title
    ) -> UpdatePullRequestTitleOutput:
        """Replaces the title of a pull request.

        :param pull_request_id: The system-generated ID of the pull request.
        :param title: The updated title of the pull request.
        :returns: UpdatePullRequestTitleOutput
        :raises PullRequestDoesNotExistException:
        :raises InvalidPullRequestIdException:
        :raises PullRequestIdRequiredException:
        :raises TitleRequiredException:
        :raises InvalidTitleException:
        :raises PullRequestAlreadyClosedException:
        """
        raise NotImplementedError

    @handler("UpdateRepositoryDescription")
    def update_repository_description(
        self,
        context: RequestContext,
        repository_name: RepositoryName,
        repository_description: RepositoryDescription = None,
    ) -> None:
        """Sets or changes the comment or description for a repository.

        The description field for a repository accepts all HTML characters and
        all valid Unicode characters. Applications that do not HTML-encode the
        description and display it in a webpage can expose users to potentially
        malicious code. Make sure that you HTML-encode the description field in
        any application that uses this API to display the repository description
        on a webpage.

        :param repository_name: The name of the repository to set or change the comment or description
        for.
        :param repository_description: The new comment or description for the specified repository.
        :raises RepositoryNameRequiredException:
        :raises RepositoryDoesNotExistException:
        :raises InvalidRepositoryNameException:
        :raises InvalidRepositoryDescriptionException:
        :raises EncryptionIntegrityChecksFailedException:
        :raises EncryptionKeyAccessDeniedException:
        :raises EncryptionKeyDisabledException:
        :raises EncryptionKeyNotFoundException:
        :raises EncryptionKeyUnavailableException:
        """
        raise NotImplementedError

    @handler("UpdateRepositoryName")
    def update_repository_name(
        self, context: RequestContext, old_name: RepositoryName, new_name: RepositoryName
    ) -> None:
        """Renames a repository. The repository name must be unique across the
        calling AWS account. Repository names are limited to 100 alphanumeric,
        dash, and underscore characters, and cannot include certain characters.
        The suffix .git is prohibited. For more information about the limits on
        repository names, see
        `Limits <https://docs.aws.amazon.com/codecommit/latest/userguide/limits.html>`__
        in the AWS CodeCommit User Guide.

        :param old_name: The current name of the repository.
        :param new_name: The new name for the repository.
        :raises RepositoryDoesNotExistException:
        :raises RepositoryNameExistsException:
        :raises RepositoryNameRequiredException:
        :raises InvalidRepositoryNameException:
        """
        raise NotImplementedError
