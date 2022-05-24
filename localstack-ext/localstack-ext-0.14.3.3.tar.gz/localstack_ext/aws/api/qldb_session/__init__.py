import sys
from typing import List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from localstack.aws.api import RequestContext, ServiceException, ServiceRequest, handler

ErrorCode = str
ErrorMessage = str
IonText = str
LedgerName = str
PageToken = str
SessionToken = str
Statement = str
TransactionId = str


class BadRequestException(ServiceException):
    """Returned if the request is malformed or contains an error such as an
    invalid parameter value or a missing required parameter.
    """

    Message: Optional[ErrorMessage]
    Code: Optional[ErrorCode]


class CapacityExceededException(ServiceException):
    """Returned when the request exceeds the processing capacity of the ledger."""

    Message: Optional[ErrorMessage]


class InvalidSessionException(ServiceException):
    """Returned if the session doesn't exist anymore because it timed out or
    expired.
    """

    Message: Optional[ErrorMessage]
    Code: Optional[ErrorCode]


class LimitExceededException(ServiceException):
    """Returned if a resource limit such as number of active sessions is
    exceeded.
    """

    Message: Optional[ErrorMessage]


class OccConflictException(ServiceException):
    """Returned when a transaction cannot be written to the journal due to a
    failure in the verification phase of *optimistic concurrency control*
    (OCC).
    """

    Message: Optional[ErrorMessage]


class RateExceededException(ServiceException):
    """Returned when the rate of requests exceeds the allowed throughput."""

    Message: Optional[ErrorMessage]


class AbortTransactionRequest(TypedDict, total=False):
    """Contains the details of the transaction to abort."""


ProcessingTimeMilliseconds = int


class TimingInformation(TypedDict, total=False):
    """Contains server-side performance information for a command. Amazon QLDB
    captures timing information between the times when it receives the
    request and when it sends the corresponding response.
    """

    ProcessingTimeMilliseconds: Optional[ProcessingTimeMilliseconds]


class AbortTransactionResult(TypedDict, total=False):
    """Contains the details of the aborted transaction."""

    TimingInformation: Optional[TimingInformation]


CommitDigest = bytes


class CommitTransactionRequest(TypedDict, total=False):
    """Contains the details of the transaction to commit."""

    TransactionId: TransactionId
    CommitDigest: CommitDigest


WriteIOs = int
ReadIOs = int


class IOUsage(TypedDict, total=False):
    """Contains I/O usage metrics for a command that was invoked."""

    ReadIOs: Optional[ReadIOs]
    WriteIOs: Optional[WriteIOs]


class CommitTransactionResult(TypedDict, total=False):
    """Contains the details of the committed transaction."""

    TransactionId: Optional[TransactionId]
    CommitDigest: Optional[CommitDigest]
    TimingInformation: Optional[TimingInformation]
    ConsumedIOs: Optional[IOUsage]


class EndSessionRequest(TypedDict, total=False):
    """Specifies a request to end the session."""


class EndSessionResult(TypedDict, total=False):
    """Contains the details of the ended session."""

    TimingInformation: Optional[TimingInformation]


IonBinary = bytes


class ValueHolder(TypedDict, total=False):
    """A structure that can contain a value in multiple encoding formats."""

    IonBinary: Optional[IonBinary]
    IonText: Optional[IonText]


StatementParameters = List[ValueHolder]


class ExecuteStatementRequest(TypedDict, total=False):
    """Specifies a request to execute a statement."""

    TransactionId: TransactionId
    Statement: Statement
    Parameters: Optional[StatementParameters]


ValueHolders = List[ValueHolder]


class Page(TypedDict, total=False):
    """Contains details of the fetched page."""

    Values: Optional[ValueHolders]
    NextPageToken: Optional[PageToken]


class ExecuteStatementResult(TypedDict, total=False):
    """Contains the details of the executed statement."""

    FirstPage: Optional[Page]
    TimingInformation: Optional[TimingInformation]
    ConsumedIOs: Optional[IOUsage]


class FetchPageRequest(TypedDict, total=False):
    """Specifies the details of the page to be fetched."""

    TransactionId: TransactionId
    NextPageToken: PageToken


class FetchPageResult(TypedDict, total=False):
    """Contains the page that was fetched."""

    Page: Optional[Page]
    TimingInformation: Optional[TimingInformation]
    ConsumedIOs: Optional[IOUsage]


class StartTransactionRequest(TypedDict, total=False):
    """Specifies a request to start a transaction."""


class StartSessionRequest(TypedDict, total=False):
    """Specifies a request to start a new session."""

    LedgerName: LedgerName


class SendCommandRequest(ServiceRequest):
    SessionToken: Optional[SessionToken]
    StartSession: Optional[StartSessionRequest]
    StartTransaction: Optional[StartTransactionRequest]
    EndSession: Optional[EndSessionRequest]
    CommitTransaction: Optional[CommitTransactionRequest]
    AbortTransaction: Optional[AbortTransactionRequest]
    ExecuteStatement: Optional[ExecuteStatementRequest]
    FetchPage: Optional[FetchPageRequest]


class StartTransactionResult(TypedDict, total=False):
    """Contains the details of the started transaction."""

    TransactionId: Optional[TransactionId]
    TimingInformation: Optional[TimingInformation]


class StartSessionResult(TypedDict, total=False):
    """Contains the details of the started session."""

    SessionToken: Optional[SessionToken]
    TimingInformation: Optional[TimingInformation]


class SendCommandResult(TypedDict, total=False):
    StartSession: Optional[StartSessionResult]
    StartTransaction: Optional[StartTransactionResult]
    EndSession: Optional[EndSessionResult]
    CommitTransaction: Optional[CommitTransactionResult]
    AbortTransaction: Optional[AbortTransactionResult]
    ExecuteStatement: Optional[ExecuteStatementResult]
    FetchPage: Optional[FetchPageResult]


class QldbSessionApi:

    service = "qldb-session"
    version = "2019-07-11"

    @handler("SendCommand")
    def send_command(
        self,
        context: RequestContext,
        session_token: SessionToken = None,
        start_session: StartSessionRequest = None,
        start_transaction: StartTransactionRequest = None,
        end_session: EndSessionRequest = None,
        commit_transaction: CommitTransactionRequest = None,
        abort_transaction: AbortTransactionRequest = None,
        execute_statement: ExecuteStatementRequest = None,
        fetch_page: FetchPageRequest = None,
    ) -> SendCommandResult:
        """Sends a command to an Amazon QLDB ledger.

        Instead of interacting directly with this API, we recommend using the
        QLDB driver or the QLDB shell to execute data transactions on a ledger.

        -  If you are working with an AWS SDK, use the QLDB driver. The driver
           provides a high-level abstraction layer above this *QLDB Session*
           data plane and manages ``SendCommand`` API calls for you. For
           information and a list of supported programming languages, see
           `Getting started with the
           driver <https://docs.aws.amazon.com/qldb/latest/developerguide/getting-started-driver.html>`__
           in the *Amazon QLDB Developer Guide*.

        -  If you are working with the AWS Command Line Interface (AWS CLI), use
           the QLDB shell. The shell is a command line interface that uses the
           QLDB driver to interact with a ledger. For information, see
           `Accessing Amazon QLDB using the QLDB
           shell <https://docs.aws.amazon.com/qldb/latest/developerguide/data-shell.html>`__.

        :param session_token: Specifies the session token for the current command.
        :param start_session: Command to start a new session.
        :param start_transaction: Command to start a new transaction.
        :param end_session: Command to end the current session.
        :param commit_transaction: Command to commit the specified transaction.
        :param abort_transaction: Command to abort the current transaction.
        :param execute_statement: Command to execute a statement in the specified transaction.
        :param fetch_page: Command to fetch a page.
        :returns: SendCommandResult
        :raises BadRequestException:
        :raises InvalidSessionException:
        :raises OccConflictException:
        :raises RateExceededException:
        :raises LimitExceededException:
        :raises CapacityExceededException:
        """
        raise NotImplementedError
