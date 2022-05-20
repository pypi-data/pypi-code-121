from functools import lru_cache
import re
import json
from datetime import datetime
from dateutil.parser import isoparse

from typing import Any, DefaultDict, Tuple, Union, List

from shapely.geometry.base import BaseGeometry
from geodesic.client import raise_on_error
from geodesic.account.projects import Project, ProjectDescr, get_active_project, get_project
from geodesic.descriptors import DatetimeDescr, DictDescr, GeometryDescr, RegexDescr, StringDescr, TypeConstrainedDescr
from geodesic.entanglement.graph import Graph
from geodesic.service import ServiceClient
from geodesic.bases import APIObject
from geodesic.stac import Item
from geodesic.utils import datetime_to_utc


entanglement_client = ServiceClient("entanglement", 1)
predicates_client = ServiceClient("entanglement", 1, "predicates")

class_re = re.compile(r'^[a-zA-Z]+[a-z]*$')
qualifier_re = re.compile(r'^(?:[a-z]+[a-z\d-]*|\*)$')
name_re = re.compile(r'^(?:[a-z\d]+[a-z\d-]*)$')
char_sub_re = re.compile(r'[^a-z\d-]')
nomatch_msg = '{field} must start with a number or letter and only contain numbers,' \
              'letters, - or _ and start with a letter'

registered_object_classes = {}
valid_spatial_predicates = ['intersects', 'within', 'contains', 'near']


@lru_cache(maxsize=None)
def _get_traits_cached(traits: Tuple[str] = None) -> List[dict]:
    params = {}
    if traits is not None:
        params['traits'] = traits

    res = raise_on_error(predicates_client.get("traits", **params))
    traits = res.json().get('traits', [])
    for t in traits:
        t['predicates'] = [Predicate(name=p) for p in t.get('predicates', [])]
    return traits


def get_traits(traits: List[str] = None, refresh: bool = False) -> List[dict]:
    """
    Gets all registered traits and their predicates. A trait modifies an object class to allow
    certain kinds of connections between objects. For example, an "Observer" trait allows the
    "can-observe" predicate between two edges. If traits are specified, returns the predicates
    for each of these traits, if registered.

    Args:
        traits: a list of trait names to check
        refresh: by default, these names are cached. If you
            want to grab the latest from the server, set refresh
            to True

    Returns:
        traits: a list of dictionaries with the keys 'name' and 'predicates'. 'predicates' contains
            a list of Predicate objects for that trait.

    Example:
        >>> get_traits()
        [{'name': 'Correlator', 'predicates': [{'name': 'correlates-with']},
        {'name': 'Linker', 'predicates': [{'name': 'links']},
        {'name': 'Observer', 'predicates': ['name': 'can-observe']}]
    """
    if refresh:
        _get_traits_cached.cache_clear()
    if traits is None:
        return _get_traits_cached()
    return _get_traits_cached(tuple(traits))


@lru_cache(maxsize=None)
def _get_predicates_cached(trait: str = None) -> List['Predicate']:
    params = {}
    if trait is not None:
        params['trait'] = trait
    res = raise_on_error(predicates_client.get("", trait=trait))
    return [Predicate(**p) for p in res.json().get('predicates', [])]


def get_predicates(trait: str = None, refresh: bool = False) -> List['Predicate']:
    """
    Gets all registered predicate names (with no trait information). Good for a quick look into
    what predicate names are available to you. If a trait is specified, gets only predicates for
    that given trait.

    Args:
        trait: a trait name to check for predicate names
        refresh: by default, these names are cached. If you
            want to grab the latest from the server, set refresh
            to True
    Returns:
        a list of Predicate objects. These can be used (or copied) to form Connections
    """
    if refresh:
        _get_predicates_cached.cache_clear()

    return _get_predicates_cached(trait=trait)


def add_predicates(trait: str, predicates: List[dict]):
    r"""
    Add predicate definitions to Entanglement. Predicates must be registered under a trait name
    and can be be specified with a few additional parameters.

    A Predicate definition looks like this:
    {
        "name": "my-predicate",
        "unidirectional": False,  # default is False
        "one_to_one": False      # default is False
    }

    `name` should match the regex ^[a-z]+[a-z\-]*$, meaning it should begin with a letter and only contain
    lowercase letters and hyphens. This is primarily for uniformity when reading graphs. The name should be
    short, but descriptive. It can convey multiple meanings, but that meaning should be able to be clarified by
    specifying edge attributes.

    `unidirectional` is a boolean that makes an edge only traversible in one direction unless explicitly requested.
    Not recommended for the majority of applications. Edges are directional by default.

    `one_to_one` restricts an edge to only connect a node to exactly one other instead of to multiple nodes.
    ``

    """
    _predicates = []
    for p in predicates:
        if not isinstance(p, dict):
            raise ValueError(f'invalid predicate {p}')

    params = {
        "trait": trait,
        "predicates": _predicates
    }

    raise_on_error(predicates_client.post(**params))


def _get_project(project: Union[str, Project]) -> str:
    if project is None:
        project = get_active_project().uid
    elif not isinstance(project, (str, Project)):
        raise ValueError("unknown project {project}")
    else:
        if isinstance(project, str):
            project = get_project(project)
            project = project.uid
        else:
            project = project.uid
    return project


def get_objects(
                *,
                search: str = None,
                version_datetime: Union[str, datetime] = None,
                object_class: str = None,
                domain: str = None,
                category: str = None,
                type: str = None,
                geometry: BaseGeometry = None,
                spatial_predicate: str = 'intersects',
                distance: float = 0.0,
                project: Union[str, Project] = None,
                limit: int = 500,
                page_size: int = 500,
                as_graph: bool = False) -> List['Object']:
    """
    Search for objects in Entanglement. There are a few ways of requesting/filtering them.
    A blank query will return the first 500 nodes for a project (in order of creation).

    Args:
        search: a search string with which to query object names and descriptions. Anything
                that matches this query will be returned in the specified project.
        version_datetime: search for versions of nodes that were valid at this datetime. Defaults
                to `None` which will only search for latest nodes.
        object_class: filters the search by object class (e.g. observable, dataset, entity, etc)
        domain: filters the search by domain
        category: filters the search by category
        type: filters the search by object type
        geometry: is a spatial filter is designed, this can be any shapely geometry, GeoJSON as dict, or
                  other object with a __geo_interface__ attribute. Geometries must be in WGS84 lon/lat.
        spatial_predicate: A spatial predicate for the filter, either 'contains', 'within', 'intersects',
                           or 'near'
        distance: If the predicate is 'near', a distance, in meters, to query from the point.
        project: a Project or project name/alias to get objects for. A query can only be for a single
                 project. If you want objects for multiple projects, break up into separate queries.
        limit: The max number of objects to return (500 by default). Set to None to return everything
               matching a query (USE WITH CAUTION, GRAPHS CAN CONTAIN MANY NODES)
        page_size: The number of results per request. This shouldn't need to be changed unless you're
                   running into issues.
        as_graph: If True, will return as a Graph object instead of a list.

    Returns:
        Either a Graph or list of objects matching the query.

    """

    # Translate the project in the argument into a project name to pass to the query.
    project = _get_project(project)

    # Get all objects?
    get_all = False
    if limit is None:
        get_all = True

    # Paging and default parameters.
    page = 1
    params = {
        'page': page,
        'page_size': page_size,
        'project': project
    }

    # Basic query parameters
    if search is not None:
        params['search'] = search

    # Find object versions that were valid at a specific datetime
    if version_datetime is not None:
        # check for valid format
        if isinstance(version_datetime, str):
            params['datetime'] = datetime_to_utc(isoparse(version_datetime)).isoformat()
        elif isinstance(version_datetime, datetime):
            params['datetime'] = datetime_to_utc(version_datetime).isoformat()
        else:
            raise ValueError("version_datetime must either be RCF3339 formatted string, or datetime.datetime")

    # Geo query parameters
    if geometry is not None:
        if not isinstance(geometry, (dict, BaseGeometry)):
            raise ValueError("geometry must be either a WGS84 GeoJSON as a dict or a shapely geometry")
        if spatial_predicate not in valid_spatial_predicates:
            raise ValueError("spatial predicate not understood, "
                             f"valid spatial predicates are: {','.join(valid_spatial_predicates)}")

        spatial = {}
        if isinstance(geometry, dict):
            spatial['geometry'] = geometry
        else:
            spatial['geometry'] = geometry.__geo_interface__

        spatial['predicate'] = spatial_predicate

        if spatial_predicate == 'near':
            if spatial['geometry']['type'] != 'Point':
                raise ValueError('near predicate only works on Point types')
            spatial['distance'] = distance
        elif spatial_predicate == 'intersects':
            if spatial['geometry']['type'] != 'Polygon':
                raise ValueError('intersects only works on Polygon types')
        elif spatial_predicate == 'within':
            if spatial['geometry']['type'] != 'Polygon':
                raise ValueError('within only works on Polygon types')
        elif spatial_predicate == 'contains':
            if spatial['geometry']['type'] not in ['Polygon', 'Point']:
                raise ValueError('contains only works on Point or Polygon types')
        params['spatial'] = json.dumps(spatial)

    uri = "objects"
    if object_class is not None:
        uri = f"{uri}/{object_class.lower()}"

        if domain is not None:
            uri = f"{uri}/{domain.lower()}"
        else:
            uri = f"{uri}/*"

        if category is not None:
            uri = f"{uri}/{category.lower()}"
        else:
            uri = f"{uri}/*"

        if type is not None:
            uri = f"{uri}/{type.lower()}"

    # run the query.
    res = raise_on_error(entanglement_client.get(uri, **params))
    res_json = res.json()

    # Parse the results.
    objects = [Object(**o) for o in res_json.get('objects', [])]
    connections = [
        Connection(**c) for c in res_json.get('connections', [])
        if not c.get('predicate')['name'].startswith('~')
    ]

    # Page through extra results.
    while get_all or (len(objects) < limit):
        params['page'] += 1
        res = raise_on_error(entanglement_client.get(uri, **params))
        res_json = res.json()

        next_obj = [Object(**o) for o in res_json.get('objects', [])]
        next_conn = [
            Connection(**c)
            for c in res_json.get('connections', [])
            if not c.get('predicate')['name'].startswith('~')
        ]

        if len(next_obj) < page_size and len(next_conn) < page_size:
            objects += next_obj
            connections += next_conn
            break
        objects += next_obj
        connections += next_conn

    if as_graph:

        return Graph(nodes=objects, edges=connections)

    return objects


def add_objects(objects: list, overwrite=False, project: Union[str, Project] = None):
    """
    Add new nodes or update existing nodes.

    Args:
        objects: a list of objects to add/update. All should have the project set or
                 they will be updated from the specified project (or active project is
                 no project is specified)
        overwrite: If overwrite is True, will overwrite existing nodes, otherwise will
                   raise an exception if they exist
        project: which project to add them to.
    """
    if project is not None:
        project = _get_project(project)

    _objects = []
    for obj in objects:
        o = Object(**obj)
        o.project = project
        _objects.append(o)

    raise_on_error(
        entanglement_client.post(
            "objects",
            objects=_objects,
            project=project,
            error_on_exists=not overwrite
        )
    )


def delete_objects(objects_or_uids: list, project: Union[str, Project] = None):
    """
    Delete objects by providing a list of objects or just their UIDs.

    Args:
        objects_or_uids: a list of Objects or UID strings to delete. If this is
                         a list of Objects, the 'uid' field must be set.
        project: which project to delete them from. This is required, but
                 if left as None, will attempt to delete from existing
                 project.

    Raises:
        requests.HTTPErrror for fault.

    Note: If objects or UIDs aren't found under existing project, won't raise an exception.
    """

    project = _get_project(project)

    # If they are uids, assume they are in the specified project and try to delete
    if all([isinstance(o, str) for o in objects_or_uids]):
        uids = objects_or_uids
        raise_on_error(entanglement_client.delete("objects", uids=uids, project=project))
        return

    # If they are objects, find all projects and delete from those.
    objects_by_project = DefaultDict(list)
    for obj in objects_or_uids:
        o = Object(**obj)
        objects_by_project[o.project.uid].append(o.uid)

    for project, uids in objects_by_project.items():
        raise_on_error(entanglement_client.delete("objects", uids=uids, project=project))


def add_connections(connections: list, overwrite=False, project: Union[str, Project] = None):
    """
    Adds connections given a list of triples (Connection objects).

    Args:
        connections: list of Connections or dicts of connections to add. Every object must exist and have a UID.
        overwrite: Overwrite this edge/connection if it exists.
        project: This will overwrite the project if none is specified on a connection.

    Raises:
        requests.HTTPError for fault.
    """
    if project is not None:
        project = _get_project(project)

    connections = [Connection(**connection) for connection in connections]
    for c in connections:
        if project is None:
            if c.subject.project != c.object.project:
                raise ValueError("all objects must be within the specified or active project.")
        else:
            c.subject.project = project
            c.object.project = project

    params = {
        'connections': connections,
        'project': project,
        'overwrite': overwrite
    }

    raise_on_error(entanglement_client.post('connections', **params))


def delete_connections(connections: list, project: Union[str, Project] = None):
    """
    Deletes connections given a list of triples (Connection objects).

    Args:
        connections: list of Connections or dicts of connections to delete. Every object must exist and have a UID.
        project: This will overwrite the project if none is specified on a connection.

    Raises:
        requests.HTTPError for fault.
    """
    if project is not None:
        project = _get_project(project)

    connections = [Connection(**connection) for connection in connections]
    for c in connections:
        if project is None:
            if c.subject.project != c.object.project:
                raise ValueError("all objects must be within the specified or active project.")
        else:
            c.subject.project = project
            c.object.project = project

    params = {
        'connections': connections,
        'project': project,
    }

    raise_on_error(entanglement_client.delete_with_body('connections', **params))


def _register(object_type: type) -> None:
    global registered_types
    k = object_type.__name__.lower()
    registered_object_classes[k] = object_type


class ObjectResolver(type):
    def __call__(cls, **obj) -> 'Object':
        if cls != Object:
            return type.__call__(cls, **obj)

        global registered_object_classes

        obj_class = obj.get('class', None)
        if obj_class is None:
            obj_class = obj.get('object_class', None)
        if obj_class is None:
            cls = Object
        else:
            cls = registered_object_classes.get(obj_class.lower(), Object)
        return type.__call__(cls, **obj)


class Object(APIObject, metaclass=ObjectResolver):
    """ Object represents a node in a graph in Entanglement.

    Objects are classified by
    their class (keyword: object_class), domain, category, type, and name. These
    values uniquely identify an object. Name and class must be specified, but the rest
    can remain empty if desired. These properties help to categorize nodes that are
    similar in name, but represent different things.

    Object also has a metaclass, so calling the Object constructer may return a different
    type based on the specified `object_class` (or `class` if created using a dictionary.).

    """
    project = ProjectDescr(doc="the project/subgraph this object belongs to")
    name = RegexDescr(regex=name_re, doc="the name of this object, unique to the project")
    object_class = RegexDescr(
        regex=class_re,
        doc="the class of this object (e.g. Observable, Entity, Dataset...)",
        dict_name="class")
    domain = RegexDescr(regex=qualifier_re, default="*", doc="the domain of this object")
    category = RegexDescr(regex=qualifier_re, default="*", doc="the category of this object")
    type = RegexDescr(regex=qualifier_re, default="*", doc="the type of this object")
    description = StringDescr(doc="a text description of this object")
    geometry = GeometryDescr(doc="a geometry for this object. Can be anything, but only points/polygons are indexed")
    item = DictDescr(doc="an arbitrary dictionary of info about this object. Must be JSON serializable")

    def __init__(self, **obj):
        self._geometry = None
        self._graph = None

        # Entanglement client
        self._client = entanglement_client

        self.project = get_active_project()

        for k, v in obj.items():
            if k == 'uid':
                self._set_item('uid', v)
                continue
            if k == 'class':
                k = 'object_class'
            try:
                setattr(self, k, v)
            except AttributeError:
                self[k] = v

    def __str__(self) -> str:
        return self.full_name

    def __repr__(self) -> str:
        return self.full_name

    @property
    def full_name(self):
        """
        Full name for an object. This acts as a sort of unique identifier even before an object
        is added to Entanglement.
        """
        return f'{self.object_class.lower()}:{self.domain}:{self.category}:{self.type}:{self.name}'

    def __eq__(self, o: object) -> bool:
        return self.full_name == o.full_name

    def __hash__(self):
        """
        Return a hash so that this can be used as a node in networkx or other
        situations that require a hash
        """
        return hash(self.full_name)

    def create(self):
        """
        Create a new Object in Entanglement. This will fail if a matching object is found.

        Raises:
            requests.HTTPError: If this failed to create.
        """
        # Make sure the uid is either None or valid
        _ = self.uid

        body = {
            "error_on_exists": True,
            "rollback_on_failure": True,
            "objects": [self]
        }

        res = raise_on_error(self._client.post("objects", project=self.project.uid, **body))

        try:
            uids = res.json()['uids']
        except KeyError:
            raise KeyError("no uids returned, something went wrong")

        if len(uids) > 1:
            raise ValueError("more objects affected than requested, something unexpected happened")

        self._set_item('uid', uids[0])

    def save(self):
        """
        Updates an existing Object in Entanglement.

        Raises:
            requests.HTTPError: If this failed to save.
        """
        # Make sure the uid is either None or valid
        try:
            self.uid
        except ValueError as e:
            raise e

        body = {
            "error_on_exists": False,
            "rollback_on_failure": True,
            "objects": [self]
        }

        res = raise_on_error(self._client.post("objects", project=self.project.uid, **body))
        try:
            uids = res.json().get('uids', [])
        except KeyError:
            raise KeyError("no uids returned, something went wrong")

        if len(uids) > 1:
            raise ValueError("more objects affected than requested, something unexpected happened")
        elif len(uids) == 1:
            self._set_item('uid', uids[0])

    def load(self, uid=None) -> Any:
        """
        Load an object given a UID.

        Args:
            uid: the uid of the object. If none, checks for the uid to have been set
                 on this object.
        """
        if uid is not None:
            self._set_item('uid', uid)

        uid = self.uid
        if uid is None:
            raise ValueError("must specify the object's uid")

        res = raise_on_error(self._client.get(f"objects/{uid}", project=self.project.uid))
        obj = Object(**res.json()["objects"][0])
        self.__init__(**obj)
        return obj

    def delete(self):
        """
        Deletes this object from Entanglement.
        """
        uid = self.uid
        if uid is None:
            raise ValueError("object has no uid")

        raise_on_error(self._client.delete("objects", **{'uids': ','.join([uid]), 'project': self.project.uid}))

    def connections(self, version_datetime: Union[str, datetime] = None) -> List['Connection']:
        """
        Returns nearest neighbor connections to this object.

        Returns:
            a list of Connection objects of nearest neighbor edges.
        """
        uid = self.uid
        if uid is None:
            raise ValueError("object has no uid")

        params = {
            "project": self.project.uid,
        }

        # Find object versions that were valid at a specific datetime
        if version_datetime is not None:
            # check for valid format
            if isinstance(version_datetime, str):
                params['datetime'] = datetime_to_utc(isoparse(version_datetime)).isoformat()
            elif isinstance(version_datetime, datetime):
                params['datetime'] = datetime_to_utc(version_datetime).isoformat()
            else:
                raise ValueError("version_datetime must either be RCF3339 formatted string, or datetime.datetime")

        res = raise_on_error(self._client.get(f"connections/{uid}", **params))

        # Parse connections...
        res_json = res.json()
        connections = []
        for c in res_json.get('connections', []):
            c.pop('subject')
            conn = Connection(**dict(subject=self, **c))
            connections.append(conn)

        return connections

    def connect_with(self, predicate: 'Predicate', object: 'Object', overwrite=False) -> 'Connection':
        """
        Adds a connection from this Object to another using the specified Predicate.

        Args:
            predicate: a Predicate object defining the connection and any edge attributes.
            object: the target Object of this connection.
            overwrite: If True, will overwrite the connection, else will raise an exception.

        Returns:
            the requested Connection.
        """
        if object.project.uid != self.project.uid:
            raise ValueError("objects must be in the same project")

        conn = Connection(subject=self, predicate=predicate, object=object)
        add_connections([conn], overwrite=overwrite, project=self.project.uid)
        return conn

    @property
    def graph(self):
        """
        If this object belongs to a graph, will return that parent graph.
        """
        return self._graph

    @graph.setter
    def graph(self, g: Graph):
        """
        Set this object to belong to a graph.
        """
        if not isinstance(g, Graph):
            raise ValueError("must be added to only an geodesic.entanglement.Graph")
        self._graph = g

    @property
    def uid(self):
        """
        Get the object's UID, if set, None otherwise.
        """
        uid = self.get('uid', None)
        if uid is not None:
            if not uid.startswith('0x'):
                raise ValueError(f'{uid} is not a valid uid')
        return uid

    @staticmethod
    def from_stac(item: Item, object_class=None, **props) -> 'Object':
        """
        Derive a new Object from a STAC item.

        Args:
            item: a STAC Item
            object_class: what class should this be interpretted as (e.g. 'Entity')
            props: additional properties to be set on this object.
        """
        if not isinstance(item, (dict, Item)):
            raise ValueError("item must be a a STAC Item")
        item = Item(**item)

        if object_class is None:
            object_class = 'entity'

        obj = Object(
            object_class=object_class,
            name=Object.sanitize_name(item.id),
            geometry=item.geometry,
            item=item,
            **props
        )

        return obj

    @staticmethod
    def sanitize_name(x: str) -> str:
        return re.sub(char_sub_re, "-", x.lower())


class Observable(Object):
    pass


class Entity(Object):
    pass


class Event(Object):
    datetime = DatetimeDescr(doc="a timestamp for this Event")
    start_datetime = DatetimeDescr(doc="a start time or beginning or some time interval for this event")
    end_datetime = DatetimeDescr(doc="an end time or end or some time interval for this event")


class Property(Object):
    pass


class Link(Object):
    href = StringDescr(doc="a link to an external resource")
    media_type = StringDescr(doc="media type of the link", dict_name="media-type")


class Model(Object):
    pass


class Concept(Object):
    pass


predicate_name_re = re.compile(r'^[a-z]+[a-z\-\_]*$')


class Predicate(APIObject):
    edge_attributes = DictDescr(doc="a dictionary of edge attributes. Must be simple types like strings, ints, floats")
    name = RegexDescr(regex=name_re, doc="the name of this predicate, describes the relationship very briefly")
    domain = RegexDescr(regex=qualifier_re, doc="the domain of this predicate", default="*")
    category = RegexDescr(regex=qualifier_re, doc="the category of this predicate", default="*")
    type = RegexDescr(regex=qualifier_re, doc="the type of this predicate", default="*")

    def __init__(self, **pred):
        super().__init__()

        for k, v in pred.items():
            setattr(self, k, v)

    def __repr__(self) -> str:
        return self.full_name

    @property
    def full_name(self):
        """
        Short, readable name for this predicate.
        """
        st = f'predicate:{self.domain}:{self.category}:{self.type}:{self.name}'
        return st

    @staticmethod
    def from_full_name(full_name: str, edge_attributes=None) -> 'Predicate':
        parts = full_name.split(':')
        match = True
        for part in parts:
            if not predicate_name_re.match(part):
                match = False

        if len(parts) != 5 or not match:
            raise ValueError(r"predicate string must be of the form: 'predicate:domain:category:type:name',"
                             r" each matching the regex ^[a-z]+[a-z\-\_]*$")

        p = Predicate()
        _, domain, category, type_, name = parts
        p.domain = domain
        p.category = category
        p.type = type_
        p.name = name

        if edge_attributes is not None:
            p.edge_attributes = edge_attributes
        return p


class Connection(APIObject):
    """
    A Connection is a relationship between two objects.

    Subject -> Predicate -> Object
    """

    subject = TypeConstrainedDescr((Object, dict), doc="the subject of this connection")
    predicate = TypeConstrainedDescr((Predicate, dict), doc="the predicate of this connection")
    object = TypeConstrainedDescr((Object, dict), doc="the object of this connection")

    def __init__(self, **conn):
        super().__init__()
        self.subject = Object(**conn['subject'])
        self.predicate = Predicate(**conn['predicate'])
        self.object = Object(**conn['object'])

    def __repr__(self):
        return f'{self.subject} --{self.predicate.name}--> {self.object}'

    def create(self, overwrite: bool = False):
        add_connections([self], overwrite=overwrite)
