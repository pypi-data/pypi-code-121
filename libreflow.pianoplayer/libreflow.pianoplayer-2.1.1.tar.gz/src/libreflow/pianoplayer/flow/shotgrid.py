import shotgun_api3
import pprint
import re
from kabaret import flow
from kabaret.flow_entities.entities import Entity, Property

from ..resources.icons import flow as _


class TestShotGridConnection(flow.Action):

    _config = flow.Parent()

    def get_buttons(self):
        self.message.set('Click the button to test the connection.')
        return ['Test']
    
    def allow_context(self, context):
        return context and context.endswith('.inline')

    def run(self, button):
        try:
            self._config.ensure_connected()
        except Exception as err:
            print(err)
            self.message.set(
                '<font color=red>Connection error:</font><br>'
                '<pre>{}</pre>'.format(err)
            )
        else:
            self.message.set(
                'Connection looks <b>OK</b>.<br>' 'See console output for details.'
            )
            pprint.pprint(self._config.get_client_info())
        return self.get_result(close=False)


class ShotGridEntity(Entity):
    """
    Defines a flow entity representing a ShotGrid entity.
    """

    shotgrid_id = Property().ui(label='ShotGrid ID', hidden=True)


class ShotGridConfig(flow.Object):

    ICON = ('icons.flow', 'shotgrid')

    server_url   = flow.Param().ui(editable=False)
    login        = flow.Param().ui(editable=False, hidden=False)
    password     = flow.Param().ui(editor='password', editable=False, hidden=False)
    project_name = flow.Computed()
    project_id   = flow.IntParam().ui(label='Project ID', editable=False).watched()

    shot_name_regex = flow.Param('[^_]*_c\d{3}_(s\d{3})').ui(editable=False, hidden=True)

    test_connection = flow.Child(TestShotGridConnection)

    def __init__(self, parent, name):
        super(ShotGridConfig, self).__init__(parent, name)
        current_site = self.root().project().get_current_site()
        if current_site.use_sg_default.get():
            current_site.sg_login.set(self.root().project().admin.project_settings.sg_login.get())
            current_site.sg_password.set(self.root().project().admin.project_settings.sg_password.get())
            self.login.set(current_site.sg_login.get())
            self.password.set(current_site.sg_password.get())
            print("Default Shotgrid login")
        else:
            self.login.set(current_site.sg_login.get())
            self.password.set(current_site.sg_password.get())
            print("Custom Shotgrid login")
        self._sg_client = None
    
    def ensure_connected(self):
        if self._sg_client is None:
            self._sg_client = shotgun_api3.Shotgun(
                base_url=self.server_url.get(),
                login=self.login.get(),
                password=self.password.get(),
            )
    
    def get_client_info(self):
        return self._client().info()
    
    def _client(self):
        self.ensure_connected()
        return self._sg_client
    
    def get_shot_task(self, shot_id, task_step_name):
        task = self._client().find_one(
            'Task',
            filters=[
                ['project', 'is', {'type': 'Project', 'id': self.project_id.get()}],
                ['entity', 'is', {'type': 'Shot', 'id': shot_id}],
                ['step.Step.code', 'is', task_step_name]

            ],
            fields=[
                'sg_status_list'
            ]
        )
        
        return task
    
    def get_shot_task_status(self, shot_id, task_step_name):
        task = self.get_shot_task(shot_id, task_step_name)
        status = None

        if task is not None:
            status = task.get('sg_status_list', None)
        
        return status

    def set_shot_task_status(self, shot_id, task_step_name, task_status_name):
        task = self.get_shot_task(shot_id, task_step_name)

        if task is not None:
            self._client().update(
                'Task', task['id'], {'sg_status_list': task_status_name}
            )
        else:
            self.root().session().log_warning((
                f'No task {task_step_name} found for shot {shot_id}'
            ))

    def get_shot_duration(self, shot_id):
        shot = self._client().find_one(
            'Shot',
            filters=[
                ['project', 'is', {'type': 'Project', 'id': self.project_id.get()}],
                ['id', 'is', shot_id],
            ],
            fields=[
                'sg_frames'
            ]
        )
        return shot['sg_frames']
    
    def get_shot_comp_briefing(self, shot_id):
        shot = self._client().find_one(
            'Shot',
            filters=[
                ['project', 'is', {'type': 'Project', 'id': self.project_id.get()}],
                ['id', 'is', shot_id],
            ],
            fields=[
                'sg_briefing_compo'
            ]
        )
        return shot['sg_briefing_compo']
    
    def get_sequences_data(self):
        '''
        Returns a list of dicts describing each sequence of the
        current project, with keys:

          - shotgrid_id: the sequence ID in ShotGrid
          - name: the sequence name in the flow
        '''
        data = []
        sequences = self._client().find(
            'Sequence',
            filters=[
                ['project', 'is', {'type': 'Project', 'id': self.project_id.get()}]
            ],
            fields=['code']
        )
        
        if sequences is not None:
            data = [
                {'shotgrid_id': sequence['id'], 'name': sequence['code']}
                for sequence in sequences
            ]
        
        return data
    
    def get_shots(self, task_step_name, task_status_name):
        tasks = self._client().find(
            'Task',
            filters=[
                ['project', 'is', {'type': 'Project', 'id': self.project_id.get()}],
                ['entity', 'type_is', 'Shot'],
                ['step', 'name_is', task_step_name],
                ['sg_status_list', 'is', task_status_name]
            ],
            fields=[
                'entity',
            ],
            order=[
                { 'field_name': 'entity', 'direction': 'asc'}
            ]
        )

        shots_data = [
            {
                'id': t['entity']['id'],
                'name': t['entity']['name']
            }
            for t in tasks
        ]
        return shots_data
    
    def get_shots_data(self, sequence_id):
        '''
        Returns a list of dicts describing each shot belonging
        to the sequence with the ShotGrid ID `sequence_id` and
        matching this object's `shot_name_regex` value, with keys:

          - shotgrid_id: the shot ID in ShotGrid
          - name: the shot name in the flow
        '''
        data = []
        shots = self._client().find(
            'Shot',
            filters=[
                ['project', 'is', {'type': 'Project', 'id': self.project_id.get()}],
                ['sg_sequence', 'is', {'type': 'Sequence', 'id': sequence_id}],
            ],
            fields=['code']
        )

        if shots is not None:
            regex = self.shot_name_regex.get()

            for shot in shots:
                m = re.search(regex, shot['code'], re.IGNORECASE)

                if m is not None:
                    data.append({
                        'shotgrid_id': shot['id'],
                        'name': m.group(1)
                    })
                else:
                    self.root().session().log_warning((
                        f'ShotGrid shot {shot["code"]} (id: {shot["code"]})'
                        f'does not match the configured shot name regex.'
                    ))
        
        return data
    
    def compute_child_value(self, child_value):
        if child_value is self.project_name:
            project = self._client().find_one(
                'Project',
                filters=[['id', 'is', self.project_id.get()]],
                fields=['name']
            )
            if project is None:
                self.project_name.set(None)
            else:
                self.project_name.set(project['name'])
    
    def child_value_changed(self, child_value):
        if child_value is self.project_id:
            self.project_name.touch()
            self.touch()
        else:
            super(ShotGridConfig, self).child_value_changed(child_value)
    
    def summary(self):
        project_id = self.project_id.get()
        summary = ''

        if project_id is None:
            summary = (
                '<font color=#D5000D>A valid ShotGrid '
                'project ID must be provided</font>'
            )
        else:
            project_name = self.project_name.get()
            if project_name is None:
                summary = (
                    '<font color=#D5000D>Invalid project ID '
                    f'<b>{project_id}</b>: the project must '
                    'exists on the specified server</font>'
                )
        
        return summary
