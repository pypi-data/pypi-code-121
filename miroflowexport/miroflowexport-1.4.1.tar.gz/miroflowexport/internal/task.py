OFFSET_ZEROBASED_INDEX = 1
import uuid
import coolname

class Task:

    DEFAULT_EFFORT = 1

    def __init__(self, id = uuid.uuid4(), name = coolname.generate_slug(2), effort = 1, progress = 0.0, start = None, end = None, costs = None, color_hex_code = None):
        self._id = id
        self._name = name

        self._effort = None
        if isinstance(effort, int) and effort >= Task.DEFAULT_EFFORT:
            self._effort = effort

        self._pre = []
        self._post = []

        self._progress = progress
        self._start = start

        self._es = None
        self._lf = None

        self._color_hex_code = color_hex_code

        self.set_costs(costs)

    def __str__(self):
        return self._name

    def __effort_offset(self):
        return max(self.effort_numerical() - OFFSET_ZEROBASED_INDEX, 0)

    def id(self):
        return self._id

    def name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def effort(self):
        return self.effort_numerical()

    def effort_numerical(self):
        if not isinstance(self._effort, int):
            return Task.DEFAULT_EFFORT
        return self._effort

    def progress(self):
        return self._progress

    def set_progress(self, progress):
        self._progress = progress

    def earliest_start(self):
        if not self._es:
            if not self._pre:
                self._es = 0
                return self._es

            self._es = max([
                predecessor.earliest_start() + predecessor.effort_numerical()
                for predecessor in self._pre
            ])
        return self._es

    def latest_finish(self):
        if not self._lf:
            if not self._post:
                self._lf = self.earliest_start() + self.__effort_offset()
                return self._lf
            
            self._lf = min([
                successor.latest_finish() - successor.effort_numerical()
                for successor in self._post
            ])
        return self._lf

    def start(self):
        if self._start == None:
            return self.earliest_start()

        return self._start

    def set_start(self, start):
        self._start = start

    def set_end(self, end):
        self._log.debug("Setting finish value for task is deprecated, this is calculated by start and effort.")

    def end(self):
        return self.start() + self.__effort_offset()

    def successors(self):
        return self._post

    def predecessors(self):
        return self._pre
        
    def is_on_critical_path(self):
        return self.latest_finish() - self.earliest_start() == self.__effort_offset()

    def costs(self):
        return self._costs

    def set_costs(self, costs):
        self._costs = 0
        if isinstance(costs, int) or isinstance(costs, float):
            self._costs = costs
        else:
            try:
                self._costs = float(costs)
            except:
                pass

    def get_color(self):
        return self._color_hex_code

    def set_color(self, color_hex_code):
        self._color_hex_code = color_hex_code
            