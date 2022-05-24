# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cisco_telescope',
 'cisco_telescope.cmd',
 'cisco_telescope.instrumentations',
 'cisco_telescope.instrumentations.aiohttp',
 'cisco_telescope.instrumentations.grpc',
 'cisco_telescope.instrumentations.requests']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'argparse>=1.4.0,<2.0.0',
 'cisco-opentelemetry-specifications>=0.0.15,<0.0.16',
 'importlib-metadata>=4.11.3,<5.0.0',
 'opentelemetry-exporter-otlp>=1.10.0,<2.0.0',
 'opentelemetry-instrumentation-aiohttp-client>=0.29b0,<0.30',
 'opentelemetry-instrumentation-grpc==0.29b0',
 'opentelemetry-instrumentation-requests>=0.29b0,<0.30',
 'opentelemetry-instrumentation>=0.29b0,<0.30',
 'opentelemetry-sdk>=1.10.0,<2.0.0',
 'opentelemetry-semantic-conventions>=0.29b0,<0.30',
 'requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['telescope = cisco_telescope.cmd.trace:run',
                     'telescope-bootstrap = cisco_telescope.cmd.bootstrap:run']}

setup_kwargs = {
    'name': 'cisco-telescope',
    'version': '1.2.0',
    'description': 'Cisco Distribution for OpenTelemetry',
    'long_description': '# otel-py\n[![PIP Published Version][pip-image]][pip-url]\n[![Apache License][license-image]][license-image]\n[![Coverage][coverage-image]][coverage-url]\n\n![Trace](trace.png)\n\nThis package provides OpenTelemetry-compliant tracing to Python\napplications for the collection of distributed tracing and performance metrics in [Cisco Telescope](https://console.telescope.app/?utm_source=github).\n\n## Contents\n\n- [Installation](#installation)\n  - [Install Packages](#install-packages)\n  - [Install Dependencies](#install-dependencies)\n  - [Library initialization](#library-initialization)\n  - [OpenTelemetry Collector Configuration](#opentelemetry-collector-configuration)\n  - [Existing OpenTelemetry Instrumentation](#existing-opentelemetry-instrumentation)\n- [Supported Runtimes](#supported-runtimes)\n- [Supported Libraries](#supported-libraries)\n- [Configuration](#configuration)\n- [Getting Help](#getting-help)\n- [Opening Issues](#opening-issues)\n- [License](#license)\n\n## Installation\n\n### Requirements\n\n`Python >=3.8, <4.0`\n`pip3 >= 22.0` \n\n### Install packages\n> To install Cisco OpenTelemetry Distribution simply run:\n\n```sh\npip install cisco-telescope\n```\n\n### Install dependencies\nTo install all supported instrumentation frameworks run:\n```sh\ntelescope-bootstrap\n```\n\n\n### Library initialization\nCisco OpenTelemetry Distribution is activated and instruments the supported libraries once the `ciscoTracing.init()` has returned.\n\nTo initialize the library, you\'ll need a cisco-token, which is taken from your [Account tab on the Telescope console Settings page](https://console.telescope.app/settings/account).\n\n\n```python\nfrom cisco_telescope import tracing\n\ntracing.init(\n  service_name="<your-service-name>",\n  cisco_token="<your-cisco-token>"\n)\n```\n\n### OpenTelemetry Collector Configuration\n\nBy default, Cisco OpenTelemetry Distribution exports data directly to [Cisco Telescope\'s](https://console.telescope.app/?utm_source=github) infrastructure backend.\n**Existing** OpenTelemetery Collector is supported, the following configuration can be applied\n\n#### Configure custom trace exporter\n\nCisco OpenTelemetry Distribution supports the configuration of multiple custom exporters. Note that you will need to handle your exporter authorization.\nExample for creating OtlpGrpc Span exporter to local OpenTelemetry collector:\n\n```python\nfrom cisco_telescope import tracing, options\n\ntracing.init(\n  service_name="<your-service-name>",\n  exporters=[\n    options.ExporterOptions(\n      exporter_type="otlp-grpc",\n      collector_endpoint="grpc://localhost:4317"\n    ),\n  ]\n)\n\n```\n\n#### Configure custom OpenTelemetry collector to export trace data to [Cisco Telescope\'s](https://console.telescope.app/?utm_source=github) external collector.\n\n```yaml\ncollector.yaml ...\n\nexporters:\n  otlphttp:\n    traces_endpoint: https://production.cisco-udp.com/trace-collector\n    headers:\n      authorization: Bearer <Your Telescope Token>\n    compression: gzip\n\n\nservice:\n  pipelines:\n    traces:\n      exporters: [otlphttp]\n```\n\n### Existing OpenTelemetry Instrumentation\n\n> Notice: Only relevant if interested in streaming existing OpenTelemetry workloads.\n> [Cisco Telescope](https://console.telescope.app/?utm_source=github). supports native OpenTelemetery traces.\n```python\nfrom opentelemetry import trace\nfrom opentelemetry.sdk.resources import Resource\nfrom opentelemetry.sdk.trace import TracerProvider\nfrom opentelemetry.sdk.trace.export import BatchSpanProcessor\n\nfrom opentelemetry.exporter.otlp.proto.http.trace_exporter import (\n    OTLPSpanExporter as OTLPHTTPExporter,\n)\n\nprovider = TracerProvider(resource=Resource.create())\ntrace.set_tracer_provider(provider)\n\nhttp_exporter = OTLPHTTPExporter(\n  endpoint="https://production.cisco-udp.com/trace-collector",\n  headers= {\n    "authorization": "Bearer <Your Telescope Token>",\n  },\n)\n\nprocessor = BatchSpanProcessor(http_exporter)\nprovider.add_span_processor(processor)\n```\n\n## Supported Runtimes\nCisco OpenTelemetry Distribution supports Python 3.6+\n\n## Supported Libraries\n\n> Cisco OpenTelemetry Python Distribution is extending Native OpenTelemetry, supported libraries [available here](https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation).\n\nCisco OpenTelemetry Python Distribution provides out-of-the-box instrumentation (tracing) and advanced **payload collections** for many popular frameworks and libraries.\n\n| Library  | Extended Support Version    |\n|----------|-----------------------------|\n| requests | Fully supported             |\n| aiohttp  | Fully supported             |\n| grpc     | Client/Server Unary support |\n\n## Configuration\n\nAdvanced options can be configured as a parameter to the init() method:\n\n| Parameter        | Env                    | Type    | Default       | Description                                                       |\n|------------------|------------------------| ------- |---------------| ----------------------------------------------------------------- |\n| cisco_token      | CISCO_TOKEN            | string  | -             | Cisco account token                                               |\n| service_name     | OTEL_SERVICE_NAME      | string  | `application` | Application name that will be set for traces                      |\n| debug            | CISCO_DEBUG            | string  | `False`       | Debug logs                                                        |\n| payloads_enabled | CISCO_PAYLOADS_ENABLED | string  | `True`        | Debug logs                                                        |\n\nExporter options\n\n| Parameter          | Env                     | Type                | Default                                               | Description                                                                                                                                |\n|--------------------| ----------------------- | ------------------- | ----------------------------------------------------- |--------------------------------------------------------------------------------------------------------------------------------------------|\n| collector_endpoint | OTEL_COLLECTOR_ENDPOINT | string              | `https://production.cisco-udp.com/trace-collector` | The address of the trace collector to send traces to                                                                                       |\n| type               | OTEL_EXPORTER_TYPE      | string              | `otlp-http`                                           | The exporter type to use (Currently only `otlp-http` is supported). Multiple exporter option available via init function see example below |\n\n## Getting Help\n\nIf you have any issue around using the library or the product, please don\'t hesitate to:\n\n- Use the [documentation](https://docs.telescope.app).\n- Use the help widget inside the product.\n- Open an issue in GitHub.\n\n## License\n\nProvided under the Apache 2.0. See LICENSE for details.\n\nCopyright 2022, Cisco\n\n[pip-url]: https://pypi.org/project/cisco-telescope/\n[pip-image]: https://img.shields.io/github/v/release/cisco-open/otel-py?include_prereleases&style=for-the-badge\n[license-url]: https://github.com/https://github.com/cisco-open/otel-py/blob/main/LICENSE\n[license-image]: https://img.shields.io/badge/license-Apache_2.0-green.svg?style=for-the-badge\n[coverage-url]: https://codecov.io/gh/cisco-open/otel-py/branch/main/\n[coverage-image]: https://img.shields.io/codecov/c/github/cisco-open/otel-py?style=for-the-badge\n',
    'author': 'Cisco Epsagon Team',
    'author_email': 'support@epsagon.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cisco-open/otel-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
