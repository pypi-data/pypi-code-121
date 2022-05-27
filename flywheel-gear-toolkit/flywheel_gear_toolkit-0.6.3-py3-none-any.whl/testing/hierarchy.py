"""Hierachy related fixtures."""
import copy
import random

import pytest

try:
    import flywheel
except (ImportError, ModuleNotFoundError) as e:
    raise ValueError(
        "This module requires flywheel-sdk, please install the `flywheel` extra."
    ) from e

rand = random.Random()

hex_choices = "abcdef0123456789"


def make_object_id():
    """Generate flywheel object id."""
    # Twelve byte hex
    return "".join(rand.choices(hex_choices, k=24))


@pytest.fixture
def object_id():
    """Wrapper for `make_object_id` as a fixture."""
    return make_object_id


def make_file_id():
    """Generate flywheel file id."""
    parts = [8, 4, 4, 4, 12]
    return "-".join(["".join(rand.choices(hex_choices, k=part)) for part in parts])


@pytest.fixture
def file_id():
    """Wrapper for `make_file_id` as a fixture."""
    return make_file_id


class MockFinder:
    """Class to mock finder object."""

    def __init__(self, arr):
        self.arr = arr

    def iter(self):
        for x in self.arr:
            yield x

    def iter_find(self, *args, **kwargs):
        yield from self.iter()

    def find(self, *args, **kwargs):
        return self.arr

    def find_first(self, *args, **kwargs):
        return self.arr[0]

    def __len__(self):
        return len(self.arr)

    def __call__(self):
        return self.arr


def make_finder(arr):
    """Create a mocked Finder from an array of objects."""
    return MockFinder(arr)


@pytest.fixture
def finder():
    """Wrapper for `make_finder` as a fixture."""
    return make_finder


class MockContainerMixin:
    """Mixin class for Mocked containers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.analyses = []
        self.files = []
        self._update = (
            None  # to store updates made to the container when calling `update`
        )

    def reload(self):
        if self._update:
            for k, v in self._update.items():
                setattr(self, k, v)
            self._update = None
        return self

    def update(self, *args, **kwargs):
        self._update = flywheel.util.params_to_dict("update", args, kwargs)
        return None

    def get_file(self, name):
        if self.files:
            for file in self.files:
                if file.name == name:
                    return file
            return files[0]
        return None


class MockFileEntry(flywheel.FileEntry):
    """Mock a File Entry."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._parent = parent


class MockAcquisition(MockContainerMixin, flywheel.Acquisition):
    """Acquisition class."""

    files = []


class MockSession(MockContainerMixin, flywheel.Session):
    """Session class."""

    acquisitions = MockFinder([])


class MockSubject(MockContainerMixin, flywheel.Subject):
    """Subject class."""

    sessions = MockFinder([])


class MockProject(MockContainerMixin, flywheel.Project):
    """Project class."""

    subjects = MockFinder([])


default_parents = {
    "acquisition": None,
    "analysis": None,
    "group": None,
    "project": None,
    "session": None,
    "subject": None,
}


class ContainerMocker:
    """Provide a mocked `get_<container>()` in Hierarchy mocks below."""

    def __init__(self):
        self.containers = dict()

    def get_container(self, _id):
        if _id in self.containers:
            return self.containers[_id]
        else:
            raise flywheel.rest.ApiException(status=409, reason="Not Found")

    def add_container(self, container):
        self.containers[container.id] = container

    def reset(self):
        self.containers = dict()


containers_mock = ContainerMocker()


@pytest.fixture
def containers():
    """Wrapper around containers_mock."""
    return containers_mock


def make_acquisition(label, n_files=1, par=None):
    """Create acquisition with a given label, number of files, and parent."""
    parents = copy.deepcopy(default_parents)
    if par:
        parents.update(par)
    acquisition = MockAcquisition(label=label, id=make_object_id(), parents=parents)
    files = []
    for i in range(n_files):
        files.append(
            MockFileEntry(
                name=f"file-{i}",
                id=make_file_id(),
                file_id=make_object_id(),
                parent=acquisition,
            )
        )
    acquisition.files = files
    containers_mock.add_container(acquisition)
    return acquisition


@pytest.fixture
def fw_acquisition():
    """Wrapper for `make_acquisition` as a fixture."""
    return make_acquisition


def make_session(label, n_acqs=1, n_files=1, par=None):
    """Create session with label, number of acqs., number of files, and parent."""
    parents = copy.deepcopy(default_parents)
    if par:
        parents.update(par)
    session = MockSession(label=label, id=make_object_id(), parents=parents)
    acquisitions = []
    for i in range(n_acqs):
        parents.update({"session": session.id})
        acquisitions.append(
            make_acquisition(f"acq-{i}-{label}", n_files=n_files, par=parents)
        )
    session.acquisitions = MockFinder(acquisitions)
    containers_mock.add_container(session)
    return session


@pytest.fixture
def fw_session():
    """Wrapper for `make_session` as a fixture."""
    return make_session


def make_subject(label, n_ses=1, n_acqs=1, n_files=1, par=None):
    """Create subject with label, number of acqs., ses., files, and parent."""
    parents = copy.deepcopy(default_parents)
    if par:
        parents.update(par)
    subject = MockSubject(label=label, id=make_object_id(), parents=parents)
    sessions = []
    for i in range(n_ses):
        parents.update({"subject": subject.id})
        sessions.append(
            make_session(
                f"ses-{i}-{label}", n_acqs=n_acqs, n_files=n_files, par=parents
            )
        )
    subject.sessions = MockFinder(sessions)
    containers_mock.add_container(subject)
    return subject


@pytest.fixture
def fw_subject(fw_session, object_id, containers):
    """Wrapper for `make_subject` as a fixture."""
    return make_subject


def make_project(
    label="test", n_subs=1, n_ses=1, n_acqs=1, n_files=1, par={"group": "test"}
):
    """Create project with label, number of acqs., ses., subs., files, and parent."""
    parents = copy.deepcopy(default_parents)
    if par:
        parents.update(par)
    project = MockProject(label=label, id=make_object_id(), parents=parents)
    subjects = []
    for i in range(n_subs):
        parents.update({"project": project.id})
        subjects.append(
            make_subject(
                f"sub-{i}", n_ses=n_ses, n_acqs=n_acqs, n_files=n_files, par=parents
            )
        )
    project.subjects = MockFinder(subjects)
    containers_mock.add_container(project)
    return project


@pytest.fixture
def fw_project(fw_subject, object_id, containers):
    """Wrapper for `make_project` as a fixture."""
    return make_project
