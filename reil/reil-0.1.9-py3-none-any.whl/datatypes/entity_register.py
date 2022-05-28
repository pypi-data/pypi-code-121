
from typing import List, Optional


class EntityRegister:
    '''
    Create and maintain a list of registered `entities`.


    :meta private:
    '''

    def __init__(
            self, min_entity_count: int, max_entity_count: int,
            unique_entities: bool = True):
        '''
        Arguments
        ---------
        min_entity_count:
            The minimum number of `entities` needed to be registered so that
            the current `instance` is ready for interaction.

        max_entity_count:
            The maximum number of `entities` that can interact with this
            instance.

        unique_entities:
            If `True`, each `entity` can be registered only once.
        '''
        self._min_entity_count = min_entity_count
        self._max_entity_count = max_entity_count
        self._unique_entities = unique_entities
        self.clear()

    @property
    def ready(self) -> bool:
        '''
        Determine if enough `entities` are registered.

        Returns
        -------
        :
            `True` if enough `entities` are registered, else `False`.
        '''
        return len(self._id_list) >= self._min_entity_count

    def append(self, entity_name: str, _id: Optional[int] = None) -> int:
        '''
        Add a new `entity` to the end of the list.

        Parameters
        ----------
        entity_name:
            The name of the `entity` to add.

        _id:
            If provided, method tries to register the `entity` with the given
            ID.

        Returns
        -------
        :
            The ID assigned to the `entity`.

        Raises
        ------
        ValueError:
            Capacity is reached. No new `entities` can be registered.

        ValueError:
            ID is already taken.

        ValueError:
            `entity_name` is already registered with a different ID.
        '''
        id_list = self._id_list
        entity_list = self._entity_list
        if (0 < self._max_entity_count < len(id_list)):
            raise ValueError(
                'Capacity is reached. No new entities can be registered.')

        if self._unique_entities:
            if entity_name in entity_list:
                current_id = id_list[entity_list.index(entity_name)]
                if _id is None or _id == current_id:
                    return current_id
                else:
                    raise ValueError(
                        f'{entity_name} is already registered with '
                        f'ID: {current_id}.')
            elif _id in id_list:
                raise ValueError(f'{_id} is already taken.')

        elif _id in id_list:
            current_entity = entity_list[id_list.index(_id)]
            if entity_name == current_entity:
                return _id
            else:
                raise ValueError(f'{_id} is already taken.')

        new_id = _id or max(id_list, default=0) + 1

        entity_list.append(entity_name)
        id_list.append(new_id)

        return new_id

    def remove(self, _id: int):
        '''
        Remove the `entity` registered by ID=`_id`.

        Arguments
        ---------
        _id:
            ID of the `entity` to remove.
        '''
        index = self._id_list.index(_id)
        self._entity_list.remove(self._entity_list[index])
        self._id_list.remove(_id)

    def clear(self):
        '''
        Clear the list.
        '''
        self._id_list: List[int] = []
        self._entity_list: List[str] = []

    def __contains__(self, _id: int) -> bool:
        return _id in self._id_list
