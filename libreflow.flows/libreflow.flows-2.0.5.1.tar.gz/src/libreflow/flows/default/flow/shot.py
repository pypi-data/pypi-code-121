from kabaret import flow
from libreflow.baseflow.shot import ShotCollection, Shot as BaseShot, Sequence as BaseSequence
from libreflow.baseflow.task import TaskCollection


class Shot(BaseShot):
    
    tasks = flow.Child(TaskCollection).ui(
        expanded=True,
        show_filter=True
    )
    
    def ensure_tasks(self):
        """
        Creates the tasks of this shot based on the task
        templates of the project, skipping any existing task.
        """
        mgr = self.root().project().get_task_manager()

        for dt in mgr.default_tasks.mapped_items():
            if not self.tasks.has_mapped_name(dt.name()) and not dt.optional.get():
                t = self.tasks.add(dt.name())
                t.enabled.set(dt.enabled.get())
        
        self.tasks.touch()


class Shots(ShotCollection):

    def add(self, name, object_type=None):
        """
        Adds a shot to the global shot collection, and creates
        its tasks.
        """
        s = super(Shots, self).add(name, object_type)
        s.ensure_tasks()


class Sequence(BaseSequence):
    
    shots = flow.Child(Shots).ui(expanded=True)
