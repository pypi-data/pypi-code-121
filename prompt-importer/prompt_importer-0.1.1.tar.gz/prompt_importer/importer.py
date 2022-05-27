import abc
import collections
import re
import sqlite3

from beancount.core import data
from beancount.ingest import importer
import blessed


class QueueSet:
    # A queue that bumps duplicate items to the front instead of prepending them
    def __init__(self, size):
        self.size = size
        self.queue = []

    def push(self, item):
        self.queue = [item] + list(filter(lambda i: i != item, self.queue))
        self.queue = self.queue[: self.size]

    def __iter__(self):
        return iter(self.queue)


class Event(abc.ABC):
    @abc.abstractmethod
    def get_field(self, field: str) -> str:
        pass

    @abc.abstractmethod
    def get_id(self) -> str:
        pass

    @abc.abstractmethod
    def display(self) -> str:
        pass

    @abc.abstractmethod
    def get_transaction(
        self, filename: str, index: int, recipient_account: str
    ) -> data.Transaction:
        pass


class PromptImporter(importer.ImporterProtocol, abc.ABC):
    def __init__(self, db_file):
        self.db_file = db_file

    @abc.abstractmethod
    def get_events(self, f) -> list[Event]:
        pass

    def prompt(self):
        return input(">> ")

    def extract(self, f):
        con = sqlite3.connect(self.db_file)
        cur = con.cursor()

        event_id_table_name = f"{self.name()}_id"
        regex_table_name = f"{self.name()}_regex"

        id_columns = f"(event_id text, recipient text, skip integer)"
        cur.execute(f"CREATE TABLE if not exists {event_id_table_name} {id_columns}")

        regex_columns = f"(field text, regex text, recipient text, skip integer)"
        cur.execute(f"CREATE TABLE if not exists {regex_table_name} {regex_columns}")

        id_mappings = list(cur.execute(f"SELECT * FROM {event_id_table_name}"))
        regex_mappings = list(cur.execute(f"SELECT * FROM {regex_table_name}"))

        known_recipients = collections.Counter(
            [m[1] for m in id_mappings] + [m[2] for m in regex_mappings]
        )

        top_known_recipients = {}
        for index, (kr, _) in enumerate(known_recipients.most_common(3)):
            top_known_recipients[str(index + 1)] = kr

        num_top_known_recipients = len(top_known_recipients)

        new_id_mappings = []
        new_regex_mappings = []

        recent_recipients = QueueSet(3)
        txns = []
        print_txns = True
        term = blessed.Terminal()
        for index, event in enumerate(self.get_events(f)):
            recipient_account = None
            skip_event = False

            for event_id, recipient, skip in id_mappings + new_id_mappings:
                if event.get_id() == event_id:
                    if skip:
                        skip_event = True
                    else:
                        recipient = recipient
                    break

            if recipient_account is None and not skip_event:
                for field, regex, recipient, skip in (
                    regex_mappings + new_regex_mappings
                ):

                    # SQLite adds additional escapes, remove them here
                    r = re.compile(regex.replace("\\\\", "\\"))
                    if re.fullmatch(r, event.get_field(field)):
                        if skip:
                            skip_event = True
                        else:
                            recipient_account = recipient
                        break

            if recipient_account is None:
                print_txns = False
                skip_char = "x"

                print(term.home + term.clear)
                print(event.display())
                print(
                    f"What should the recipient account be? ('{skip_char}' to not extract a transaction)"
                )

                for rr_index, rr in enumerate(recent_recipients):
                    top_known_recipients[
                        str(num_top_known_recipients + rr_index + 1)
                    ] = rr

                known_recipients_message = ""
                for label, kr in top_known_recipients.items():
                    known_recipients_message += f"{label}. {kr}   "
                print(known_recipients_message)

                recipient_account = self.prompt().strip()

                if recipient_account in top_known_recipients:
                    recipient_account = top_known_recipients[recipient_account]

                if recipient_account == skip_char:
                    skip_event = True
                else:
                    recent_recipients.push(recipient_account)

                print(
                    f"What regex should identify this account (or skip) in the future? ('{skip_char}' to not identify this accoung with a regex)"
                )
                identify_regex = self.prompt().strip()

                if identify_regex == skip_char:
                    if recipient_account == skip_char:
                        new_id_mappings.append((event.get_id(), "skip", 1))
                    else:
                        new_id_mappings.append((event.get_id(), recipient_account, 0))
                else:
                    print(f"What field should the regex act upon?")
                    target_field = self.prompt().strip()

                    if recipient_account == skip_char:
                        new_regex_mappings.append(
                            (target_field, identify_regex, "skip", 1)
                        )
                    else:
                        new_regex_mappings.append(
                            (target_field, identify_regex, recipient_account, 0)
                        )

            if print_txns and not skip_event:
                txns.append(event.get_transaction(f.name, index, recipient_account))

        if new_id_mappings:
            query = f"INSERT INTO {event_id_table_name} VALUES"
            for new_id_mapping in new_id_mappings:
                query += f"\n{new_id_mapping},"
            cur.execute(query[:-1])
            con.commit()

        if new_regex_mappings:
            query = f"INSERT INTO {regex_table_name} VALUES"
            for new_regex_mapping in new_regex_mappings:
                query += f"\n{new_regex_mapping},"
            cur.execute(query[:-1])
            con.commit()

        con.close()

        if print_txns:
            return txns
        else:
            return []
