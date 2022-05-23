"""
`check_api_client`
=======================================================================
Functional tests for the api client

* Author(s): Bryan Siepert
"""
#!/usr/bin/env python
from logging import getLogger
import embedops_cli.api as client
from embedops_cli.config import settings

# Configure API key authorization: ApikeyAuth
_logger = getLogger(__file__)
configuration = client.Configuration()

configuration.api_key["X-API-Key"] = settings.api_repo_key
configuration.host = f"{settings.host}/api/v1"

# create an instance of the API class
api_instance = client.ApiClient(configuration)
body = client.CIRunCreateProps(
    branch="pipline-elements",
    commit_id="49384853c0ca826f143a37b17df09eeaf01a6f63",
    type="unittest",
)

ci_run = api_instance.create_ci_run_from_ci(body)

_logger.info("created CI run:")
_logger.info(ci_run)

metric_attrs = client.MetricCreateProps(
    ci_run_id=ci_run.id,
    name="ram_size",
    value=1099,
    dimensions={"build_target": "debug"},
)
ci_run_id = ci_run.id
name = "ram_size"
value = 1099
dimensions = {"build_target": "debug"}

new_metric = api_instance.create_metric_from_ci(metric_attrs)
_logger.info("created new metric: %s", new_metric)

type = "junit"
data = "junit-metrics-on-suite-withfails.xml"
api_response = api_instance.upload_ci_run_artifact(type, data, ci_run_id)

_logger.info(api_response)
_logger.info("finishing:")
_logger.info("setting CI run status to success")

body = client.CIRunUpdateProps()  # CIRunUpdateProps | Data to update the CIRun
body.status = "success"
ci_run = api_instance.update_ci_run_from_ci(body, ci_run_id=ci_run.id)

_logger.info("\nresponse:")
_logger.info(ci_run)
del api_instance
