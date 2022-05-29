from fabrique_atelier.actors import Processor, Dispatcher, Pipeline
from fabrique_atelier.constants import MessageFieldsConstants as fld
import json

colors = ['clear', 'red', 'green', 'blue']
repaint_rule = {'red': 'magenta', 'green': 'yellow', 'blue': 'cyan'}

serialize_data = lambda data: json.dumps(data).encode()
deserialize_data = lambda ser_data: json.loads(ser_data)


class BalloonDispatcher(Dispatcher):
    def get_result(self, mes):
        data = deserialize_data(mes[fld.data])
        color = data['color']
        color_num = colors.index(color)  # can raise value errors

        mes[fld.metrics] = {'color': color_num}

        if color in repaint_rule:
            data['decision'] = 'repainted'
            mes[fld.destination] = self.destinations.balloon_repainter
            mes[fld.data] = data  # we expect easy and fast hidden serialization
            return mes

        data['decision'] = 'passed'
        mes[fld.destination] = self.destinations.end
        mes[fld.data] = serialize_data(data)  # we expect json in output topic
        return mes


def repaint_and_serialize(mes):
    new_color = repaint_rule[mes['data']['color']]
    repainted = 0
    if mes[fld.data]['color'] != new_color:
        repainted = 1
        mes[fld.data]['color'] = new_color
    mes[fld.data] = serialize_data(mes['data'])
    mes[fld.metrics] = {'repainted': repainted}
    return mes


class BalloonRepainter(Processor):
    # noinspection PyMethodMayBeStatic
    def get_batch_result(self, batch):
        return [repaint_and_serialize(mes) for mes in batch]



pipeline = Pipeline(['balloon_dispatcher', 'balloon_repainter'])

ids = pipeline.ids
nodes = pipeline.nodes

nodes.balloon_dispatcher = BalloonDispatcher.to(ids.end, ids.balloon_repainter)
nodes.balloon_repainter = BalloonRepainter.to(ids.end)
