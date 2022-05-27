from ikologikapi.dataiterator.GraphDataIteratorMeter import GraphDataIteratorMeter


class GraphDataIterator:
    def __init__(self, installation, start_date, end_date, api):
        self.installation = installation
        self.start_date = start_date
        self.end_date = end_date
        self.current_date = None
        self.graph_data_meter_map = {}
        self.counter = 0
        self.initialized = False
        self.api = api

    def add_meters(self, meters):
        for meter in meters:
            self.graph_data_meter_map[meter["id"]] = GraphDataIteratorMeter(self.installation, meter["id"])

    def init(self):
        for key, graph_data_iterator_meter in self.graph_data_meter_map.items():
            graph_data_iterator_meter.start_date = self.start_date
            graph_data_iterator_meter.end_date = self.end_date
            graph_data_iterator_meter.api = self.api

        self.initialized = True
        return self

    def has_next(self):
        if not self.initialized:
            return False

        for key, graph_data_iterator_meter in self.graph_data_meter_map.items():
            if graph_data_iterator_meter.has_next():
                return True

    def next(self):
        if not self.initialized:
            return False

        self.counter += 1

        date = None
        for key, graph_data_iterator_meter in self.graph_data_meter_map.items():

            if graph_data_iterator_meter.has_next():
                date = self.get_earliest_date(date, graph_data_iterator_meter.peek().date)

        for key, graph_data_iterator_meter in self.graph_data_meter_map.items():
            if graph_data_iterator_meter.has_next() and graph_data_iterator_meter.peek().date == date:
                graph_data_iterator_meter.next()

        self.current_date = date

    def get_meter_data(self, meter_id):
        if not self.initialized:
            return False

        graph_data_iterator_meter = self.graph_data_meter_map.get(meter_id)

        if graph_data_iterator_meter.current_data and self.current_date == graph_data_iterator_meter.current_data.date:
            return graph_data_iterator_meter.current_data

        return None

    def get_earliest_date(self, date1, date2):
        if date1 is None and date2 is None:
            return None
        elif date1 is not None and date2 is None:
            return date1
        elif date1 is None and date2 is not None:
            return date2
        else:
            if date1 > date2:
                return date1
            else:
                return date2


