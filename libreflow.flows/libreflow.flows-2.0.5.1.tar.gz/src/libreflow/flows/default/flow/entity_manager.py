from kabaret import flow
from libreflow.utils.kabaret.flow_entities.entities import GlobalEntityCollection
from libreflow.utils.flow import ActionValueStore
from libreflow.baseflow.entity_manager import EntityManager as BaseEntityManager


class EntityManager(BaseEntityManager):

    films              = flow.Child(GlobalEntityCollection)
    sequences          = flow.Child(GlobalEntityCollection)
    shots              = flow.Child(GlobalEntityCollection)
    tasks              = flow.Child(GlobalEntityCollection)
    files              = flow.Child(GlobalEntityCollection)
    revisions          = flow.Child(GlobalEntityCollection)
    sync_statutes      = flow.Child(GlobalEntityCollection)
    
    action_value_store = flow.Child(ActionValueStore)

    def get_film_collection(self):
        return self.films
    
    def get_sequence_collection(self):
        return self.sequences

    def get_shot_collection(self):
        return self.shots
    
    def get_task_collection(self):
        return self.tasks

    def get_file_collection(self):
        return self.files
    
    def get_revision_collection(self):
        return self.revisions
    
    def get_sync_status_collection(self):
        return self.sync_statutes
