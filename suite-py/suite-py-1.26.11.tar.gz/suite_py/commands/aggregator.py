# -*- coding: utf-8 -*-
import re
import sys

from halo import Halo
from kubernetes import client, config
from rich.console import Console
from rich.table import Table

from suite_py.lib import logger
from suite_py.lib.handler import prompt_utils
from suite_py.lib.handler.captainhook_handler import CaptainHook


class Aggregator:
    def __init__(self, config, command):
        self._captainhook = CaptainHook(config)
        self._command = command

    def run(self):
        if self._command == "list":
            self._list_aggregators()
            return

        if self._command == "change":
            aggregator = self._select_aggregator()
            address = prompt_utils.ask_questions_input(
                "Insert QA url or press enter to set staging URL: ",
                default_text="staging.prima.it",
            )

            if address.startswith("http"):
                address = re.sub(r"https?://?", "", address)

            split_addr = re.split(r"([a-z]+)\-([a-z0-9]+)", address)

            change_request = self._captainhook.change_aggregator(
                aggregator["name"], address
            )

            self._handle_captainhook_response(
                change_request, aggregator["name"], address
            )

            if "www" in split_addr:
                split_addr[1] = "prima"
                self._update_k8s_ingress_route(aggregator, split_addr[1], split_addr[2])
            elif "evvivass" in split_addr:
                self._update_k8s_ingress_route(aggregator, split_addr[1], split_addr[2])
            else:
                return

    def _handle_captainhook_response(self, request, aggregator, address):
        if request.status_code == 200:
            change_request = request.json()
            if change_request["success"]:
                logger.info(f"CNAME updated! Now {aggregator} is pointing to {address}")
            else:
                cases = {
                    "cloudflare_error": "Error during Cloudflare invocation.",
                    "unknown_dns_record": "Impossible to find DNS record associated with aggregator.",
                    "unknown_aggregator": "Aggregator not found.",
                    "invalid_qa_address": "The QA address does not meet the requirements.",
                }
                logger.error(cases.get(change_request["error"], "unknown error"))
                sys.exit(-1)
        else:
            logger.error("An error has occurred on Captainhook.")
            sys.exit(-1)

    def _select_aggregator(self):
        with Halo(text="Loading aggregators...", spinner="dots", color="magenta"):
            choices = [
                {"name": agg["name"], "value": agg}
                for agg in self._captainhook.aggregators().json()
            ]
        if choices:
            choices.sort(key=lambda x: x["name"])
            return prompt_utils.ask_choices("Select aggregator: ", choices)

        logger.error("There are no aggregators on Captainhook.")
        sys.exit(-1)

    def _list_aggregators(self):
        with Halo(text="Loading...", spinner="dots", color="magenta"):
            aggregators = self._captainhook.aggregators()

        if aggregators.status_code != 200:
            logger.error("Unable to retrieve the list of aggregators.")
            return

        console = Console()

        aggregators_table = Table()
        aggregators_table.add_column("Name", style="green")
        aggregators_table.add_column("Address", style="white")

        for a in aggregators.json():
            aggregators_table.add_row(a["name"], a["content"])

        logger.info("Available aggregators:")
        console.print(aggregators_table)

    def _update_k8s_ingress_route(self, aggregator, service_name, namespace):
        try:
            config.load_kube_config()
        except Exception:
            logger.error(
                "\n\nYou need to authenticate, run the following command:\n$ aws eks update-kubeconfig --name main-qa\n\n"
            )
            sys.exit(-1)

        api = client.CustomObjectsApi()
        res = {
            "apiVersion": "traefik.containo.us/v1alpha1",
            "kind": "IngressRoute",
            "metadata": {
                "name": f"{aggregator['name']}",
                "namespace": f"{namespace}",
                "annotations": {
                    "traefik.ingress.kubernetes.io/router.tls": "true",
                },
                "labels": {
                    "com.prima.environment": "qa",
                    "com.prima.country": "it",
                    "app.kubernetes.io/name": f"{aggregator['name']}",
                },
            },
            "spec": {
                "entryPoints": ["websecure"],
                "routes": [
                    {
                        "kind": "Rule",
                        "match": f"Host(`{aggregator['address']}{aggregator['domain']}`)",
                        "services": [{"name": f"{service_name}", "port": 80}],
                    }
                ],
            },
        }

        try:
            api.create_namespaced_custom_object(
                group="traefik.containo.us",
                version="v1alpha1",
                namespace=namespace,
                plural="ingressroutes",
                body=res,
            )
            logger.info(f"Aggregator {aggregator['name']} created!")
        except Exception:
            api.patch_namespaced_custom_object(
                group="traefik.containo.us",
                version="v1alpha1",
                namespace=namespace,
                plural="ingressroutes",
                name=aggregator["name"],
                body=res,
            )
            logger.info(f"Aggregator {aggregator['name']} updated!")
