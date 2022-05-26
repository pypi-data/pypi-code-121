"""
A python client for the [Projectal API](https://projectal.com/docs/latest).

## Getting started

```
import projectal
import os

# Supply your Projectal server URL and account credentials
projectal.api_base = https://yourcompany.projectal.com/
projectal.api_username = os.environ.get('PROJECTAL_USERNAME')
projectal.api_password = os.environ.get('PROJECTAL_PASSWORD')

# Test communication with server
status = projectal.status()

# Test account credentials
projectal.login()
details = projectal.auth_details()
```

----

## Changelog

### 2.0.2
- Fixed updating Webhook entities

### 2.0.1
- Fixed application ID not being used correctly.

### 2.0.0
- Version 2.0 accompanies the release of Projectal 2.0. There are no major changes
  since the previous release.
- Expose `Entity.changes()` function. It returns a list of fields on an entity that
  have changed since fetching it. These are the changes that will be sent over to the
  server when an update request is made.
- Added missing 'packaging' dependency to requirements.

### 1.2.0

**Breaking changes**:

- Renamed `request_timestamp` to `response_timestamp` to better reflect its purpose.
- Automatic timestamp conversion into dates (introduced in `1.1.0`) has been reverted.
  All date fields returned from the server remain as UTC timestamps.

  The reason is that date fields on tasks contain a time component and converting them
  into date strings was erasing the time, resulting in a value that does not match
  the database.

  Note: the server supports setting date fields using a date string like `2022-04-05`.
  You may use this if you prefer but the server will always return a timestamp.

  Note: we provide utility functions for easily converting dates from/to
  timestamps expected by the Projectal server. See:
  `projectal.date_from_timestamp()`,`projectal.timestamp_from_date()`, and
  `projectal.timestamp_from_datetime()`.

**Other changes**:
- Implement request chunking - for methods that consume a list of entities, we now
  automatically batch them up into multiple requests to prevent timeouts on really
  large request. Values are configurable through
  `projectal.chunk_size_read` and `projectal.chunk_size_write`.
  Default values: Read: 1000 items. Write: 200 items.
- Added profile get/set functions on entities for easier use. Now you only need to supply
  the key and the data. E.g:

```
key = 'hr_connector'
data = {'staff_source': 'company_z'}
task.profile_set(key, data)
```

- Entity link methods now automatically update the entity's cached list of links. E.g:
  a task fetched with staff links will have `task['staffList'] = [Staff1,Staff2]`.
  Before, doing a `task.link_staff(staff)` did not modify the list to reflect the
  addition. Now, it will turn into `[Staff1,Staff2,Staff3]`. The same applies for update
  and delete.

  This allows you to modify links and continue working with that object without having
  to fetch it again to obtain the most recent link data. Be aware that if you acquire
  the object without requesting the link data as well
  (e.g: `projectal.Task.get(id, links='STAFF')`),
  these lists will not accurately reflect what's in the database, only the changes made
  while the object is held.

- Support new `applicationId` property on login. Set with: `projectal.api_application_id`.
  The application ID is sent back to you in webhooks so you know which application was
  the source of the event (and you can choose to filter them accordingly).
- Added `Entity.set_readonly()` to allow setting values on entities that will not
  be sent over to the server when updating/saving the entity.

  The main use case for this is to populate cached entities which you have just created
  with values you already know about. This is mainly a workaround for the limitation of
  the server not sending the full object back after creating it, resulting in the client
  needing to fetch the object in full again if it needs some of the fields set by the
  server after creation.

  Additionally, some read-only fields will generate an error on the server if
  included in the update request. This method lets you set these values on newly
  created objects without triggering this error.

  A common example is setting the `projectRef` of a task you just created.


### 1.1.1
- Add support for 'profiles' API. Profiles are a type of key-value storage that target
  any entity. Not currently documented.
- Fix handling error message parsing in ProjectalException for batch create operation
- Add `Task.update_order()` to set task order
- Return empty list when GETing empty list instead of failing (no request to server)
- Expose the timestamp returned by requests that modify the database. Use
  `projectal.request_timestamp` to get the value of the most recent request (None
  if no timestamp in response)

### 1.1.0
- Minimum Projectal version is now 1.9.4.

**Breaking changes**:
- Entity `list()` now returns a list of UUIDs instead of full objects. You may provide
  an `expand` parameter to restore the previous behavior: `Entity.list(expand=True)`.
  This change is made for performance reasons where you may have thousands of tasks
  and getting them all may time out. For those cases, we suggest writing a query to filter
  down to only the tasks and fields you need.
- `Company.get_master_company()` has been renamed to `Company.get_primary_company()`
  to match the server.
- The following date fields are converted into date strings upon fetch:
  `startTime`, `closeTime`, `scheduleStart`, `scheduleFinish`.
  These fields are added or updated using date strings (like `2022-03-02`), but the
  server returns timestamps (e.g: 1646006400000) upon fetch, which is confusing. This
  change ensures they are always date strings for consistency.

**Other changes**:
- When updating an entity, only the fields that have changed are sent to the server. When
  updating a list of entities, unmodified entities are not sent to the server at all. This
  dramatically reduces the payload size and should speed things up.
- When fetching entities, entity links are now typed as well. E.g. `project['rebateList']`
  contains a list of `Rebate` instead of `dict`.
- Added `date_from_timestamp()` and `timestamp_from_date()` functions to help with
  converting to/from dates and Projectal timestamps.
- Entity history now uses `desc` by default (index 0 is newest)
- Added `Project.tasks()` to list all task UUIDs within a project.

### 1.0.3
- Fix another case of automatic JWT refresh not working

### 1.0.2
- Entity instances can `save()` or `delete()` on themselves
- Fix broken `dict` methods (`get()` and `update()`) when called from Entity instances
- Fix automatic JWT refresh only working in some cases

### 1.0.1
- Added `list()` function for all entities
- Added search functions for all entities (match-, search, query)
- Added `Company.get_master_company()`
- Fixed adding template tasks

"""
import os

from projectal.entities import *
from .api import *
from . import profile

api_base = os.getenv('PROJECTAL_URL')
api_username = os.getenv('PROJECTAL_USERNAME')
api_password = os.getenv('PROJECTAL_PASSWORD')
api_application_id = None
cookies = None
chunk_size_read = 1000
chunk_size_write = 200

# Records the timestamp generated by the last request (database
# event time). These are reported on add or updates; if there is
# no timestamp in the response, this is set to None.
response_timestamp = None


# The minimum version number of the Projectal instance that this
# API client targets. Lower versions are not supported and will
# raise an exception.
MIN_PROJECTAL_VERSION = "2.0.0"
