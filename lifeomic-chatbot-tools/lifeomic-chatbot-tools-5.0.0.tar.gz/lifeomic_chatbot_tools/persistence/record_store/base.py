import operator
import typing as t


TId_co = t.TypeVar("TId_co", covariant=True)


class IRecord(t.Protocol[TId_co]):
    def get_id(self) -> TId_co:
        ...


TIRecord = t.TypeVar("TIRecord", bound=IRecord)
TId_contra = t.TypeVar("TId_contra", contravariant=True)
T = t.TypeVar("T")
operators = {"<=": operator.le, ">=": operator.ge, "<": operator.lt, ">": operator.gt, "==": operator.eq}


class IRecordStore(t.Protocol[TId_contra, T]):
    """Interface for a Data Access Object (DAO) which can save objects to some back-end persistence solution."""

    def save(self, record: T):
        """Updates ``record`` in the database, or creates it if it's not there."""
        ...

    def get(self, id_: TId_contra) -> t.Optional[T]:
        """Retrieves a record from the database, returning ``None`` if it doesn't exist."""
        ...

    def delete(self, id_: TId_contra) -> bool:
        """
        Deletes a record from the database, returning ``True`` if the record was deleted, and ``False`` if it didn't
        exist.
        """
        ...

    def get_all(self, *conditions: t.Tuple[str, str, t.Any], **where_equals) -> t.Iterable[T]:
        """Retrieves all records which satisfy the optional conditions."""
        ...

    def delete_all(self, *conditions: t.Tuple[str, str, t.Any], **where_equals) -> int:
        """
        Deletes all records which satisfy the optional conditions. Returns the number of records that were deleted.
        """
        ...
