import logging
import uuid
from datetime import datetime
from typing import List

import pytz
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import subqueryload
from txcelery.defer import DeferrableTask

from peek_plugin_base.worker import CeleryDbConn
from peek_core_user._private.server.controller.PasswordUpdateController import (
    PasswordUpdateController,
)
from peek_core_user._private.storage.InternalGroupTuple import (
    InternalGroupTuple,
)
from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_core_user._private.tuples.InternalUserImportResultTuple import (
    InternalUserImportResultTuple,
)
from peek_plugin_base.worker.CeleryApp import celeryApp
from peek_core_user.tuples.import_.ImportInternalUserTuple import (
    ImportInternalUserTuple,
)
from vortex.Payload import Payload

logger = logging.getLogger(__name__)


@DeferrableTask
@celeryApp.task(bind=True)
def importInternalUsers(
    self, importHash: str, usersVortexMsg: bytes
) -> InternalUserImportResultTuple:
    """Import Internal Users

    :param self: A celery reference to this task
    :param importHash: An unique string of this group of items being imported.
    :param usersVortexMsg: A vortexMsg containing the user tuples
    :returns: A list of grid keys that have been updated.
    """

    importUsers: List[ImportInternalUserTuple] = (
        Payload().fromEncodedPayload(usersVortexMsg).tuples
    )

    startTime = datetime.now(pytz.utc)

    session = CeleryDbConn.getDbSession()
    try:
        same = []
        updates = []
        deleteIds = []
        inserts = []
        errors = []

        # This will remove duplicates
        allUuids = [i.userUuid for i in importUsers]

        if not allUuids:
            existingUsersByUuid = {}

        else:
            existingUsersByUuid = {
                g.userUuid: g
                for g in session.query(InternalUserTuple)
                .filter(InternalUserTuple.userUuid.in_(allUuids))
                .filter(InternalUserTuple.importHash == importHash)
                .options(subqueryload(InternalUserTuple.groups))
                .all()
            }

        groupsByName = {
            g.groupName: g for g in session.query(InternalGroupTuple).all()
        }

        for importUser in importUsers:
            try:
                existingUser = existingUsersByUuid.pop(
                    importUser.userUuid, None
                )
                if existingUser:
                    _updateUser(
                        existingUser, groupsByName, importUser, same, updates
                    )

                else:
                    _insertUser(
                        session, groupsByName, importUser, importHash, inserts
                    )

                session.commit()

            except IntegrityError as e:
                errors.append(str(e))
                session.rollback()

        for oldUser in existingUsersByUuid.values():
            deleteIds.append(oldUser.id)
            session.delete(oldUser)

        session.commit()

        logger.info(
            "Inserted %s, Updated %s, Deleted %s, Same %s, in %s",
            len(inserts),
            len(updates),
            len(deleteIds),
            len(same),
            (datetime.now(pytz.utc) - startTime),
        )

        return InternalUserImportResultTuple(
            addedIds=[o.id for o in inserts],
            updatedIds=[o.id for o in updates],
            deletedIds=deleteIds,
            sameCount=len(same),
            errors=errors,
        )

    except Exception as e:
        session.rollback()
        logger.debug("Task failed, but it will retry. %s", e)
        raise self.retry(exc=e, countdown=2)

    finally:
        session.close()


def _insertUser(session, groupsByName, importUser, importHash, inserts):
    newUser = InternalUserTuple()
    newUser.importHash = importHash

    for fieldName in ImportInternalUserTuple.tupleFieldNames():
        value = getattr(importUser, fieldName)
        if fieldName == "userName":
            # fill 'userKey' as well
            setattr(newUser, "userKey", value.lower())
        setattr(newUser, fieldName, value)

    if importUser.groupKeys is not None:
        for groupKey in importUser.groupKeys:
            newUser.groups.append(groupsByName[groupKey])

    newUser.password = PasswordUpdateController.hashPass(str(uuid.uuid4()))

    session.add(newUser)
    inserts.append(newUser)


def _updateUser(existingUser, groupsByName, importUser, same, updates):
    excludeFieldNames = ("groupKeys", "password", "userUuid")

    copyFields = filter(
        lambda f: f not in excludeFieldNames,
        ImportInternalUserTuple.tupleFieldNames(),
    )

    updated = False
    for fieldName in copyFields:
        newVal = getattr(importUser, fieldName)
        existingVal = getattr(existingUser, fieldName)
        if existingVal != newVal:
            if existingVal and not newVal:
                """ Don't wipe out values if they already exist """

            else:
                setattr(existingUser, fieldName, newVal)
                # update userKey as well when 'userName' changes
                if fieldName == "userName":
                    setattr(existingUser, "userKey", newVal.lower())
                updated = True

    # The password is an optional field
    if importUser.password is not None:
        existingUser.password = PasswordUpdateController.hashPass(
            importUser.password
        )
        updated = True

    # If there are NONE groups, then don't make any changes
    if importUser.groupKeys is not None:
        linkedGroupNames = set([g.groupName for g in existingUser.groups])
        addGroups = set(importUser.groupKeys) - linkedGroupNames
        removeGroups = linkedGroupNames - set(importUser.groupKeys)

        for addGroup in addGroups:
            existingUser.groups.append(groupsByName[addGroup])

        for removeGroup in removeGroups:
            existingUser.groups.remove(groupsByName[removeGroup])

        updated = updated or bool(addGroups) or bool(removeGroups)

    if updated:
        updates.append(existingUser)
    else:
        same.append(existingUser)
