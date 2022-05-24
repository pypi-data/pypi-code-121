import argparse


class TestOptions():
    """Options class
    Returns:
        [argparse]: argparse containing Test options
    """

    def __init__(self):
        ##
        self.parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.parser.add_argument(
            '--database', type=str,
            help="database name")
        self.parser.add_argument(
            '--username', type=str,
            help="username for database")
        self.parser.add_argument(
            '--password', type=str,
            help="password for database")
        self.parser.add_argument(
            '--host', type=str,
            help="host for database")
        self.parser.add_argument(
            '--port', type=str,
            help="port for database")
        self.parser.add_argument(
            '--DataSetPath', type=str,
            help='Path to data set (outer path)',
            required=True)
        self.parser.add_argument(
            '--query', type=str,
            help='query for retrieving data',
            required=True)
        self.parser.add_argument(
            '--table_name', type=str,
            help="table_name in database")
        self.parser.add_argument(
            '--output_directory', type=str,
            help='output directory for experiment (preds and tensorboard)',
            required=True)
        self.parser.add_argument(
            '--create_tensorboard_timestamp', type=bool,
            help='optional to create tensorboard timestamp for debug',
            default=False)
        self.parser.add_argument("--cpu", type=str,
                                 default="False", help="Use cpu? ")
        self.parser.add_argument(
            '--num_workers', type=int,
            default=2,
            help='number of workers (cpus) for prefetching')
        self.parser.add_argument(
            '--datasetFingerprintFile', type=str,
            help='Path to dataset fingerprint yaml file')
        self.parser.add_argument(
            '--TestSize', type=float,
            default=0.2,
            help='Proportion of dataset used for testing')
        self.parser.add_argument(
            '--use_DDP', type=str,
            help='use distributed data paralele? "TRUE" is yes',
            default="True")
        self.parser.add_argument(
            "--local_rank", type=int,
            help="Local rank: torch.distributed.launch.")    

    def parse(self):
        """ Parse Arguments.
        """
        self.opt = self.parser.parse_args()
        return self.opt


class TrainOptions(TestOptions):
    """Options class
    Returns:
        [argparse]: argparse containing Train options
    """

    def __init__(self):
        super(TrainOptions, self).__init__()

        self.parser.add_argument(
            '--config', type=str,
            help='Path to the YAML config file',
            required=True),


    def parse(self):
        """ Parse Arguments.
        """
        self.opt = self.parser.parse_args()
        return self.opt
