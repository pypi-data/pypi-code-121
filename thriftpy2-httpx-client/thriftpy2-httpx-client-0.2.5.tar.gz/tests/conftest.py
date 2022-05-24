import multiprocessing
import time
from typing import Dict, List

from pkg_resources import resource_filename as rsc_fn

import pytest

import thriftpy2
from thriftpy2.http import make_server

thriftpy2.install_import_hook()

addressbook = thriftpy2.load(
    path=rsc_fn(__name__, 'resources/addressbook.thrift'),
    module_name='addressbook_thrift',
)


class Dispatcher:
    def __init__(self):
        self.ab = addressbook.AddressBook()
        self.ab.people = {}

    def ping(self):
        return True

    def hello(self, name: str) -> str:
        return f"hello {name}"

    def add(self, person: addressbook.Person) -> bool:
        self.ab.people[person.name] = person
        return True

    def remove(self, name: bool) -> bool:
        try:
            del self.ab.people[name]
            return True
        except KeyError:
            raise addressbook.PersonNotExistsError(f"{name} not exists")

    def get(self, name: str) -> addressbook.Person:
        try:
            return self.ab.people[name]
        except KeyError:
            raise addressbook.PersonNotExistsError(f"{name} not exists")

    def book(self) -> addressbook.AddressBook:
        return self.ab

    def get_phonenumbers(self,
                         name: str,
                         count: int) -> List[addressbook.PhoneNumber]:
        try:
            return [self.ab.people[name].phones[0]] * count
        except KeyError:
            return []

    def get_phones(self, name: str) -> Dict[int, addressbook.PhoneNumber]:
        try:
            return {p.type: p.number for p in self.ab.people[name].phones}
        except KeyError:
            return {}

    def sleep(self, ms: int) -> bool:
        time.sleep(ms / 1000)
        return True


@pytest.fixture
def addressbook_thrift():
    return addressbook


@pytest.fixture(scope="session", autouse=True)
def server(request):
    server = make_server(
        addressbook.AddressBookService,
        Dispatcher(),
        host="127.0.0.1",
        port=6080,
    )
    ps = multiprocessing.Process(target=server.serve)
    ps.start()

    time.sleep(0.1)

    def fin():
        if ps.is_alive():
            ps.terminate()
    request.addfinalizer(fin)


@pytest.fixture(scope="session")
def person():
    phone1 = addressbook.PhoneNumber()
    phone1.type = addressbook.PhoneType.MOBILE
    phone1.number = '555-1212'
    phone2 = addressbook.PhoneNumber()
    phone2.type = addressbook.PhoneType.HOME
    phone2.number = '555-1234'

    # empty struct
    phone3 = addressbook.PhoneNumber()

    alice = addressbook.Person()
    alice.name = "Alice"
    alice.phones = [phone1, phone2, phone3]
    alice.created_at = int(time.time())

    return alice
