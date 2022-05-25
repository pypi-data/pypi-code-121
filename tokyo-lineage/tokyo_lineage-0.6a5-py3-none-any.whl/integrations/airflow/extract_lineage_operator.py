import logging
from typing import Optional, Tuple, Type, List, Callable, Any

from airflow.operators import BaseOperator
from airflow.utils.decorators import apply_defaults

from tokyo_lineage.extractor.airflow_extractor import AirflowExtractor
from tokyo_lineage.metadata_extractor.base import BaseMetadataExtractor
from tokyo_lineage.utils.airflow import get_dagruns

class ExtractLineageOperator(BaseOperator):
    
    template_fields = ()
    ui_color = '#fee8f4'

    @apply_defaults
    def __init__(
        self,
        dagrun_filters: Optional[Tuple] = (),
        dagrun_filters_with_context: Optional[List[Callable[[Any], Tuple]]] = None,
        custom_metadata_extractors: Optional[List[Type[BaseMetadataExtractor]]] = None,
        openlineage_conn_id: Optional[str] = None,
        *args,
        **kwargs):
        super(ExtractLineageOperator, self).__init__(*args, **kwargs)
        self.dagrun_filters = dagrun_filters
        self.dagrun_filters_with_context = dagrun_filters_with_context
        self.custom_metadata_extractors = custom_metadata_extractors
        self.openlineage_conn_id = openlineage_conn_id
    
    def execute(self, context):
        logging.info("Start extracting lineage")

        logging.info("Scanning Airflow DagRun")
        dagrun_filters = self.dagrun_filters

        if self.dagrun_filters_with_context:
            # Providing context to dagrun_filters_with_context
            dagrun_filters_with_context = [f(context) for f in self.dagrun_filters_with_context]

            for f in dagrun_filters_with_context:
                dagrun_filters = dagrun_filters + tuple(list(f))

        dagruns = get_dagruns(*dagrun_filters)

        logging.info("Instantiating extractor")
        extractor = AirflowExtractor(
                        self.custom_metadata_extractors,
                        self.openlineage_conn_id)

        logging.info("Calling JobRun handler")
        extractor.handle_jobs_from_dagrun(dagruns)

        logging.info("Finished extracting lineage")
        logging.info("INFO: Processed {} jobs".format(len(dagruns)))