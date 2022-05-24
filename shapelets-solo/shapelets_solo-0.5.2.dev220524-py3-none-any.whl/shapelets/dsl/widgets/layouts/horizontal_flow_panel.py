from shapelets.dsl.widgets import Widget, AttributeNames
from shapelets.dsl.widgets.layouts.panel import Panel


class HorizontalFlowPanel(Panel):
    """
    TO BE FILLED
    """

    def __init__(self, panel_title: str = None,
                 panel_id: str = None,
                 **additional):
        super().__init__(panel_title=panel_title, panel_id=panel_id, **additional)
        self.placements = dict()

    def place(self, widget: Widget, width: int = 1, offset: int = 0):
        super()._place(widget)
        self.placements[widget.widget_id] = (width, offset)

    def to_dict_widget(self):
        panel_dict = super().to_dict_widget()
        panel_dict[AttributeNames.PROPERTIES.value].update({
            AttributeNames.PLACEMENTS.value: [{
                AttributeNames.WIDGET_REF.value: key,
                AttributeNames.WIDTH.value: width,
                AttributeNames.OFFSET.value: offset
            } for key, (width, offset) in self.placements.items()]
        })
        return panel_dict
