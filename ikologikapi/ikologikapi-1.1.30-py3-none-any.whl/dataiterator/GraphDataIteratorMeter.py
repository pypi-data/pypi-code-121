from ikologikapi.domain.GraphData import GraphData


class GraphDataIteratorMeter:
    def __init__(self, installation, meter_id):
        self.installation = installation
        self.meter_id = meter_id
        self.start_date = None
        self.end_date = None
        self.current_data = None
        self.data_buffer = None
        self.has_more_data = True
        self.api = None

    def has_next(self):
        self.load_more_data()
        return True if self.data_buffer and len(self.data_buffer) > 0 else False

    def peek(self):
        if not self.has_next():
            return None

        return self.data_buffer[0]

    def next(self):
        if not self.has_next():
            return None

        self.current_data = self.data_buffer[0]
        self.data_buffer.pop(0)
        return self.current_data

    def load_more_data(self):
        converted_list = []
        if self.data_buffer is None:
            data_list = self.api.graph.get_graph_data(self.installation, self.meter_id, 'DATA', self.start_date, self.end_date, 50)

            if (data_list is None or len(data_list) == 0) or len(data_list) < 50:
                self.has_more_data = False

            for obj in data_list:
                converted_list.append(
                    GraphData(obj[0], obj[1])
                )

            self.data_buffer = converted_list
        elif self.has_more_data and len(self.data_buffer) == 1:
            data_list = self.api.graph.get_graph_data(self.installation, self.meter_id, 'DATA', self.data_buffer[0].date, self.end_date, 50)

            if (data_list is None or len(data_list) == 0) or len(data_list) < 50:
                self.has_more_data = False

            for obj in data_list:
                converted_list.append(
                    GraphData(obj[0], obj[1])
                )

            self.data_buffer = converted_list

