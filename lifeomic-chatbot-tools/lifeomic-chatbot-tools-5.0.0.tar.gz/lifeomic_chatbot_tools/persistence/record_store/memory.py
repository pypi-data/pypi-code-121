import typing as t

from lifeomic_chatbot_tools.persistence.record_store.base import IRecordStore, TIRecord, operators


THashable = t.TypeVar("THashable", bound=t.Hashable)


class InMemoryRecordStore(t.Generic[THashable, TIRecord], IRecordStore[THashable, TIRecord]):
    r"""
    A simple in-memory DAO for Pydantic data models. Useful for testing or other lightweight needs. Does not keep any
    indexes of non-primary key fields, so `WHERE` clause queries are :math:`\mathcal{O}(n)`.
    """

    def __init__(self):
        # Records in the db can be resolved via `self._db[id]`.
        self._db: t.Dict[THashable, TIRecord] = {}

    def save(self, record: TIRecord):
        self._db[record.get_id()] = record

    def get(self, id_: THashable) -> t.Optional[TIRecord]:
        return self._db.get(id_)

    def delete(self, id_: THashable) -> bool:
        if self.get(id_) is not None:
            del self._db[id_]
            return True
        return False

    def get_all(self, *conditions: t.Tuple[str, str, t.Any], **where_equals) -> t.Iterable[TIRecord]:
        for record in self._db.values():
            if self._matches(record, *conditions, **where_equals):
                yield record

    def delete_all(self, *conditions: t.Tuple[str, str, t.Any], **where_equals) -> int:
        to_delete = [id_ for id_, record in self._db.items() if self._matches(record, *conditions, **where_equals)]
        for id_ in to_delete:
            del self._db[id_]
        return len(to_delete)

    @staticmethod
    def _matches(record: TIRecord, *conditions: t.Tuple[str, str, t.Any], **where_equals) -> bool:
        all_conditions = list(conditions) + [(k, "==", v) for k, v in where_equals.items()]
        return all(operators[op](getattr(record, k), v) for k, op, v in all_conditions)
