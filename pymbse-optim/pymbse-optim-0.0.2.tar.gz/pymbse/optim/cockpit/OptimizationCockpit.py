from IPython.display import display

from pymbse.optim.cache_database_api import get_list_of_best_generation_ix_individual_ix_score, get_max_optimization_ix
from pymbse.optim.cockpit.OptimizationCockpitWidget import OptimizationCockpitWidget
from pymbse.optim.cockpit.PeriodicTimer import PeriodicTimer


class OptimizationCockpit:
    """ Class displaying and refreshing the optimization cockpit.

    """
    def __init__(self,
                 ip_with_port_cache: str,
                 optimization_ix: int = None,
                 is_log_y=False) -> None:
        """ Constructor of the OptimizationCockpit class

        :param ip_with_port_cache:
        :param optimization_ix:
        :param is_log_y: if True, then the score plot has logarithmic y-scale
        """
        self.ip_with_port_cache = ip_with_port_cache
        max_optimization_ix = get_max_optimization_ix(ip_with_port_cache)
        if optimization_ix is None:
            self.optimization_ix = max_optimization_ix
        else:
            if optimization_ix > max_optimization_ix:
                raise AttributeError('The provided optimization index %d is greater than the maximum one in the db %d.'
                                     % (optimization_ix, max_optimization_ix))
            else:
                self.optimization_ix = optimization_ix
        self.is_log_y = is_log_y
        self.widget = None
        self.logger_df = get_list_of_best_generation_ix_individual_ix_score(self.ip_with_port_cache,
                                                                            self.optimization_ix)

    def display(self, t_sleep_in_sec=5.0) -> None:
        """ Method displaying the cockpit and starting a timer to refresh the cockpit with a given period.

        :param t_sleep_in_sec: the refresh interval for the cockpit
        """
        if len(self.logger_df):
            self.widget = OptimizationCockpitWidget(self.ip_with_port_cache,
                                                    self.optimization_ix,
                                                    self.logger_df,
                                                    self.is_log_y)
            self.widget.build()
            display(self.widget.show())

            PeriodicTimer(t_sleep_in_sec, self.update_cockpit)
        else:
            raise Warning('The logger dataframe is empty, no data to display!')

    def update_cockpit(self) -> None:
        """ Method updating the cockpit by checking whether an update is available, i.e., the logger was populated with
        new information.

        """
        logger_new_df = get_list_of_best_generation_ix_individual_ix_score(self.ip_with_port_cache,
                                                                           self.optimization_ix)

        if len(logger_new_df) > len(self.logger_df):
            self.logger_df = logger_new_df
            self.widget.min_logger_df = logger_new_df
            self.widget.widget.data = []
            self.widget.build()
