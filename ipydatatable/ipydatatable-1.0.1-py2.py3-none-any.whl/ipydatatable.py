import ipywidgets as widgets
from traitlets import List as _List, TraitType as _TraitType, Type as _Type, Any as _Any, Unicode as _Unicode, Bool as _Bool, Int as _Int, validate as _validate, TraitError as _TraitError
from .table_traitlet import DataTable as _DataTable

# See js/lib/ipydatatable.js for the frontend counterpart to this file.

@widgets.register
class InteractiveTable(widgets.DOMWidget):
    """
        Widget for an interactive table utilizing jquery datatable. Column named
        "group" with a dictionary inside will be used for creating child rows
        for tables that are hidden until expanded. 

        Parameters:
            - table: 
                contains the data to be displayed. This can be in the form of a
                Pandas dataframe, a dictionary or a list. (required)
            - column_filter: 
                Allows to display a section for filtering per column. 
                Default to True. (optional)
            - text_limit: 
                Number of characters to display per column. If the data 
                is too much, an elipsis appears and you can access the whole
                information in a child dropdown. The search will not work on
                the text that has been reduced. Default to 1000. (optional)
            - sort_column: 
                Column to sort by on initalization. Takes a string with the
                name of the column to sort by. (optional)
            - columns: 
                Array od column names used to hide/show columns from the  
                beginningof display. To determine if to hide or show you use 
                the init_state parameter. (optional)
            - init_state: 
                Parameter to detemine to show or hide the columns passed 
                in the columns parameter. Allowed values: "show" or 
                "hide". (optional)
            - selected_data: 
                Conatains an array with the data from the rows seleted  
                on the table. This is a traitlet and can be monitored for 
                updates. (optional)
            - selected_index_row: 
                Array of the index of the rows selected in the table.
                This is also used to initialize the dataframe with 
                selected rows from the beginning. This gets updated
                when rows are selected. (optional)
            - child_group_select: 
                Boolean that makes the values of the dictionary of 
                group into buttons that can be selected. A way to 
                make a more specific selection option than Just a 
                row. Defeaults  to False. (optional)
            
    """

    # Name of the widget view class in front-end
    _view_name = _Unicode('InteractiveTableView').tag(sync=True)

    # Name of the widget model class in front-end
    _model_name = _Unicode('InteractiveTableModel').tag(sync=True)

    # Name of the front-end module containing widget view
    _view_module = _Unicode('ipydatatable').tag(sync=True)

    # Name of the front-end module containing widget model
    _model_module = _Unicode('ipydatatable').tag(sync=True)

    # Version of the front-end module containing widget view
    _view_module_version = _Unicode('^1.0.1').tag(sync=True)
    # Version of the front-end module containing widget model
    _model_module_version = _Unicode('^1.0.1').tag(sync=True)

    # Widget specific property.
    # Widget properties are defined as traitlets. Any property tagged with `sync=True`
    # is automatically synced to the frontend *any* time it changes in Python.
    # It is synced back to Python from the frontend *any* time the model is touched.
    table = _DataTable([]).tag(sync=True)
    column_filter = _Bool(True).tag(sync=True)
    child_group_select = _Bool(False).tag(sync=True)
    text_limit = _Int(1000).tag(sync=True)
    sort_column = _Unicode("None").tag(sync=True)
    selected_group = _DataTable([]).tag(sync=True)
    selected_data = _DataTable([]).tag(sync=True)
    selected_index_row = _DataTable([]).tag(sync=True)
    columns = _DataTable([]).tag(sync=True)
    init_state = _Unicode("hide").tag(sync=True)

    # Basic validator for the floater value
    @_validate('init_state')
    def _valid_filter(self, proposal):
        if isinstance(proposal['value'], str):
            if proposal['value'] == "show" or proposal['value'] == "hide":
                return proposal['value']
            else:
                raise _TraitError('Invalid column filter value. Approriate values are show or hide')
        raise _TraitError('Invalid column filter value. Provide a string.')

    # Basic validator for the floater value
    @_validate('column_filter')
    def _valid_filter(self, proposal):
        if isinstance(proposal['value'], bool):
            return proposal['value']
        raise _TraitError('Invalid column filter value. Provide a boolean.')

    # Basic validator for the floater value
    @_validate('child_group_select')
    def _valid_child_select(self, proposal):
        if isinstance(proposal['value'], bool):
            return proposal['value']
        raise _TraitError('Invalid child group select value. Provide a boolean.')

    # Basic validator for the label value
    @_validate('text_limit')
    def _valid_text_limit(self, proposal):
        if isinstance(proposal['value'], int):
            return proposal['value']
        raise _TraitError('Invalid text limit value. Provide an int.')

    # Basic validator for the icon value
    @_validate('sort_column')
    def _valid_sort_column(self, proposal):
        if isinstance(proposal['value'], str):
            return proposal['value']
        raise _TraitError('Invalid sort column value. Provide a string.')

    def innotebook():
        import subprocess
        output = subprocess.getoutput('jupyter nbextension list')
        if 'ipydatatable/extension \x1b[32m enabled' not in output:
            print('Enable ipydatatable extension by running "jupyter nbextension enable --py --sys-prefix ipydatatable" in a terminal and refresh screen')
        else:
            print("ipydatatable: If no table displayed on initialization, please refresh window.")

    innotebook()

    def get_selected_groups(self):
        data = {}
        for x in self.selected_group:
            split = x.split(":")
            if split[0] in data.keys():
                data[split[0]][split[1]] = split[2]
            else:
                data[split[0]] = {split[1]:split[2]}
                
        return data
