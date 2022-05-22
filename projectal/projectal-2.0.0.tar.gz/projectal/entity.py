"""
The base Entity class that all entities inherit from.
"""

import projectal
from projectal import api


class Entity(dict):
    """
    The parent class for all our entities, offering requests
    and validation for the fundamental create/read/update/delete
    operations.

    This class (and all our entities) inherit from the builtin
    `dict` class. This means all entity classes can be used
    like standard Python dictionary objects, but we can also
    offer additional utility functions that operate on the
    instance itself (see `linkers` for an example). Any method
    that expects a `dict` can also consume an `Entity` subclass.

    The class methods in this class can operate on one or more
    entities in one request. If the methods are called with
    lists (for batch operation), the output returned will also
    be a list. Otherwise, a single `Entity` subclass is returned.

    Note for batch operations: a `ProjectalException` is raised
    if *any* of the entities fail during the operation. The
    changes will *still be saved to the database for the entities
    that did not fail*.
    """

    #: Child classes must override these with their entity names
    _path = 'entity'
    _name = 'ENTITY'

    def __init__(self, data):
        dict.__init__(self, data)
        self.get = self.__get
        self.update = self.__update
        self.delete = self.__delete
        self.__type_link_lists()
        self.__old = dict(self)

    @classmethod
    def create(cls, entities, params=None):
        """
        Create one or more entities of the same type. The entity
        type is determined by the subclass calling this method.

        `entities`: Can be a `dict` to create a single entity,
        or a list of `dict`s to create many entities in bulk.

        `params`: Optional URL parameters that may apply to the
        entity's API (e.g: `?holder=1234`).

        If input was a `dict`, returns an entity subclass. If input was
        a list of `dict`s, returns a list of entity subclasses.

        ```
        # Example usage:
        projectal.Customer.create({'name': 'NewCustomer'})
        # returns Customer object
        ```
        """
        if isinstance(entities, dict):
            # Dict input needs to be a list
            payload = [entities]
        else:
            # We have a list of dicts already, the expected format
            payload = entities
        endpoint = '/api/{}/add'.format(cls._path)
        if params:
            endpoint += params
        if not payload:
            return []

        objects = []
        for i in range(0, len(payload), projectal.chunk_size_write):
            chunk = payload[i:i + projectal.chunk_size_write]
            response = api.post(endpoint, chunk)
            # Put uuId from response into each input dict
            for e, o in zip(chunk, response):
                e['uuId'] = o['uuId']
                objects.append(cls(e))

        if not isinstance(entities, list):
            return objects[0]
        return objects

    @classmethod
    def get(cls, entities, links=None):
        """
        Get one or more entities of the same type. The entity
        type is determined by the subclass calling this method.

        `entities`: One of several formats containing the `uuId`s
        of the entities you want to get (see bottom for examples):

        - `str` or list of `str`
        - `dict` or list of `dict` (with `uuId` key)

        `links`: Optional URL parameter to request entity links
        as part of the response (e.g: `?links=COMPANY,LOCATION,`).
        For performance reasons, links are only returned on demand.

        Links follow a common naming convention in the output with
        a *_List* suffix. E.g.:
        `?links=COMPANY,LOCATION` will appear as `companyList` and
        `locationList` in the response.

        ```
        # Example usage:
        # str
        projectal.Project.get('1b21e445-f29a-4a9f-95ff-fe253a3e1b11')

        # list of str
        ids = ['1b21e445-f29a...', '1b21e445-f29a...', '1b21e445-f29a...']
        projectal.Project.get(ids)

        # dict
        project = project.Project.create({'name': 'MyProject'})
        # project = {'uuId': '1b21e445-f29a...', 'name': 'MyProject', ...}
        projectal.Project.get(project)

        # list of dicts (e.g. from a query)
        # projects = [{'uuId': '1b21e445-f29a...'}, {'uuId': '1b21e445-f29a...'}, ...]
        project.Project.get(projects)

        # str with links
        projectal.Project.get('1b21e445-f29a...', 'links=COMPANY,LOCATION')
        ```
        """

        if isinstance(entities, str):
            # String input is a uuId
            payload = [{'uuId': entities}]
        elif isinstance(entities, dict):
            # Dict input needs to be a list
            payload = [entities]
        elif isinstance(entities, list):
            # List input can be a list of uuIds or list of dicts
            # If uuIds (strings), convert to list of dicts
            if len(entities) > 0 and isinstance(entities[0], str):
                payload = [{'uuId': uuId} for uuId in entities]
            else:
                # Already expected format
                payload = entities
        else:
            # We have a list of dicts already, the expected format
            payload = entities

        url = '/api/{}/get'.format(cls._path)
        if links:
            url += '?links={}'.format(links)
        # We only need to send over the uuIds
        payload = [{'uuId': e['uuId']} for e in payload]
        if not payload:
            return []
        objects = []
        for i in range(0, len(payload), projectal.chunk_size_read):
            chunk = payload[i:i + projectal.chunk_size_read]
            dicts = api.post(url, chunk)
            objects.extend([cls(d) for d in dicts])
        if not isinstance(entities, list):
            return objects[0]
        return objects

    def __get(self, *args, **kwargs):
        """Use the dict get for instances."""
        return super(Entity, self).get(*args, **kwargs)

    @classmethod
    def update(cls, entities):
        """
        Save one or more entities of the same type. The entity
        type is determined by the subclass calling this method.
        Only the fields that have been modifier will be sent
        to the server as part of the request.

        `entities`: Can be a `dict` to update a single entity,
        or a list of `dict`s to update many entities in bulk.

        Returns `True` if all entities update successfully.

        ```
        # Example usage:
        rebate = projectal.Rebate.create({'name': 'Rebate2022', 'rebate': 0.2})
        rebate['name'] = 'Rebate2024'
        projectal.Rebate.update(rebate)
        # Returns True. New rebate name has been saved.
        ```
        """
        if isinstance(entities, dict):
            e_list = [entities]
        else:
            e_list = entities

        # Reduce the list to only modified entities and their modified fields.
        # Only do this to an Entity subclass - the consumer may have passed
        # in a dict of changes on their own.
        payload = []
        for e in e_list:
            if isinstance(e, Entity):
                changes = e.changes()
                if changes:
                    changes['uuId'] = e['uuId']
                    payload.append(changes)
            else:
                payload.append(e)
        if payload:
            for i in range(0, len(payload), projectal.chunk_size_write):
                chunk = payload[i:i + projectal.chunk_size_write]
                api.put('/api/{}/update'.format(cls._path), chunk)
        return True

    def __update(self, *args, **kwargs):
        """Use the dict update for instances."""
        return super(Entity, self).update(*args, **kwargs)

    def save(self):
        """Calls `update()` on this instance of the entity, saving
        it to the database."""
        return self.__class__.update(self)

    @classmethod
    def delete(cls, entities):
        """
        Delete one or more entities of the same type. The entity
        type is determined by the subclass calling this method.

        `entities`: See `Entity.get()` for expected formats.

        ```
        # Example usage:
        ids = ['1b21e445-f29a...', '1b21e445-f29a...', '1b21e445-f29a...']
        projectal.Customer.delete(ids)
        ```
        """
        if isinstance(entities, str):
            # String input is a uuId
            payload = [{'uuId': entities}]
        elif isinstance(entities, dict):
            # Dict input needs to be a list
            payload = [entities]
        elif isinstance(entities, list):
            # List input can be a list of uuIds or list of dicts
            # If uuIds (strings), convert to list of dicts
            if len(entities) > 0 and isinstance(entities[0], str):
                payload = [{'uuId': uuId} for uuId in entities]
            else:
                # Already expected format
                payload = entities
        else:
            # We have a list of dicts already, the expected format
            payload = entities

        # We only need to send over the uuIds
        payload = [{'uuId': e['uuId']} for e in payload]
        if not payload:
            return True
        for i in range(0, len(payload), projectal.chunk_size_write):
            chunk = payload[i:i + projectal.chunk_size_write]
            api.delete('/api/{}/delete'.format(cls._path), chunk)
        return True

    def __delete(self):
        """Let an instance delete itself."""
        return self.__class__.delete(self)

    def clone(self, entity):
        """
        Clones an entity and returns its `uuId`.

        Each entity has its own set of required values when cloning.
        Check the API documentation of that entity for details.
        """
        url = '/api/{}/clone?reference={}'.format(self._path, self['uuId'])
        response = api.post(url, entity)
        return response['jobClue']['uuId']

    def history(self, start=0, limit=-1, order='desc'):
        """
        Returns an ordered list of all changes made to the entity.

        `start`: Start index for pagination (default: `0`).

        `limit`: Number of results to include for pagination. Use
        `-1` to return the entire history (default: `-1`).

        `order`: `asc` or `desc` (default: `desc` (index 0 is newest))
        """
        url = "/api/{}/history?holder={}&start={}&limit={}&order={}" \
            .format(self._path, self['uuId'], start, limit, order)
        return api.get(url)

    @classmethod
    def list(cls, expand=False, links=None):
        """Return a list of all entity UUIDs of this type.

        You may pass in `expand=True` to get full Entity objects
        instead, but be aware this may be very slow if you have
        thousands of objects.

        If you are expanding the objects, you may further expand
        the results with `links`.
        """

        payload = {
            "name": "List all entities of type {}".format(cls._name),
            "type": "msql", "start": 0, "limit": -1,
            "select": [
                ["{}.uuId".format(cls._name)]
            ],
        }
        ids = api.query(payload)
        ids = [id[0] for id in ids]
        if ids:
            return cls.get(ids, links=links) if expand else ids
        return []

    @classmethod
    def match(cls, field, term, links=None):
        """Find entities where `field`=`term` (exact match), optionally
        expanding the results with `links`.

        Relies on `Entity.query()` with a pre-built set of rules.
        ```
        projects = projectal.Project.match('identifier', 'zmb-005')
        ```
        """
        filter = [["{}.{}".format(cls._name, field), "eq", term]]
        return cls.query(filter, links)

    @classmethod
    def match_startswith(cls, field, term, links=None):
        """Find entities where `field` starts with the text `term`,
        optionally expanding the results with `links`.

        Relies on `Entity.query()` with a pre-built set of rules.
        ```
        projects = projectal.Project.match_startswith('name', 'Zomb')
        ```
        """
        filter = [["{}.{}".format(cls._name, field), "prefix", term]]
        return cls.query(filter, links)

    @classmethod
    def match_endswith(cls, field, term, links=None):
        """Find entities where `field` ends with the text `term`,
        optionally expanding the results with `links`.

        Relies on `Entity.query()` with a pre-built set of rules.
        ```
        projects = projectal.Project.match_endswith('identifier', '-2023')
        ```
        """
        term = "(?i).*{}$".format(term)
        filter = [["{}.{}".format(cls._name, field), "regex", term]]
        return cls.query(filter, links)

    @classmethod
    def search(cls, fields=None, term='', case_sensitive=True, links=None):
        """Find entities that contain the text `term` within `fields`.
        `fields` is a list of field names to target in the search.

        `case_sensitive`: Optionally turn off case sensitivity in the search.

        Relies on `Entity.query()` with a pre-built set of rules.
        ```
        projects = projectal.Project.search(['name', 'description'], 'zombie')
        ```
        """
        filter = []
        term = '(?{}).*{}.*'.format('' if case_sensitive else '?', term)
        for field in fields:
            filter.append(["{}.{}".format(cls._name, field), "regex", term])
        filter = ['_or_', filter]
        return cls.query(filter, links)

    @classmethod
    def query(cls, filter, links=None):
        """Run a query on this entity with the supplied filter.

        The query is already set up to target this entity type, and the
        results will be converted into full objects when found, optionally
        expanded with the `links` provided. You only need to supply a
        filter to reduce the result set.

        See [the filter documentation](https://projectal.com/docs/v1.1.1#section/Filter-section)
        for a detailed overview of the kinds of filters you can construct.
        """
        payload = {
            "name": "Python library entity query ({})".format(cls._name),
            "type": "msql", "start": 0, "limit": -1,
            "select": [
                ["{}.uuId".format(cls._name)]
            ],
            "filter": filter
        }
        ids = api.query(payload)
        ids = [id[0] for id in ids]
        if ids:
            return cls.get(ids, links=links)
        return []


    def profile_get(self, key):
        """Get the profile (metadata) stored for this entity at `key`."""
        return projectal.profile.get(key, self.__class__._name.lower(), self['uuId'])

    def profile_set(self, key, data):
        """Set the profile (metadata) stored for this entity at `key`. The contents
        of `data` will completely overwrite the existing data dictionary."""
        return projectal.profile.set(key, self.__class__._name.lower(), self['uuId'], data)

    def __type_link_lists(self):
        """Find lists of entity links and turn their dicts into typed
        objects matching their Entity type. Links come back in the
        ___List format. E.g., taskList, staffList etc."""

        for key in self.keys():
            if key.endswith('List'):
                entity = key.split('List')[0].capitalize()
                try:
                    cls = getattr(projectal, entity)
                except AttributeError:
                    # Could be a non-entity list. Ignore.
                    continue
                as_obj = []
                for e in self[key]:
                    as_obj.append(cls(e))
                self[key] = as_obj

    def changes(self):
        """Return a dict containing only the names of the fields that have changed."""
        changed = {}
        for key in self.keys():
            if key not in self.__old:
                changed[key] = self[key]
            elif self.__old[key] != self[key]:
                changed[key] = self[key]
        return changed

    def set_readonly(self, key, value):
        """Set a field on this Entity that will not be sent over to the
        server on update."""
        self[key] = value
        self.__old[key] = value
