#!/usr/bin/python
import json
import uuid
import os
import re
from abc import ABCMeta, abstractmethod

from sumoappclient.provider.factory import ProviderFactory
from sumoappclient.common.logger import get_logger
from sumoapputils.common.testapp import TestApp
from sumoapputils.common.utils import get_file_data, USER, get_app_config_key
import six
import click
from sumoapputils.common.testutils import get_test_class



cli_logger = get_logger(__name__, LOG_FILEPATH="/tmp/sumoapptestutils.log", LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"))

if six.PY2:
    input = raw_input

APP_CATEGORIES = ["Amazon Web Services", "Compliance and Security", "Database", "DevOps", "Google Cloud Platform",
                  "IT Infrastructure", "Kubernetes", "Microsoft Azure", "Operating System", "Storage", "Sumo Logic",
                  "Web Server", "Work from Home Solution", "Sumo Logic Certified"]

reverse_category_map = {val: i for i, val in enumerate(APP_CATEGORIES)}

APP_CATEGORY_NUM_CHOICES = "\n".join(["[%d] - %s" % (i, val) for i, val in enumerate(APP_CATEGORIES)])

@click.group()
def manifestcmd():
    pass


def validate_choice(ctx, param, value):

    try:
        values = [c.strip() for c in value.split(',')] if isinstance(value, str) else value
        num_values = map(lambda nv: int(nv), values)
        categories = list(map(lambda idx: APP_CATEGORIES[idx], num_values))
        return categories

    except IndexError:
        # If the index does not exist.
        click.echo('Please select a valid index.')

    except (TypeError, ValueError):
        # If the value is of a different type, for example, String.
        click.echo('Please select a valid value from the choices. \n\n{}\n\n'.format(APP_CATEGORY_NUM_CHOICES))

    # Prompt the user for an input.
    value = click.prompt(param.prompt)
    return validate_choice(ctx, param, value)

def validate_url(ctx, param, value):

    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    try:
        if not re.match(regex, value):
            raise ValueError(value)
        else:
            return value
    except ValueError as e:
        click.echo('Incorrect url given: {}'.format(e))
        value = click.prompt(param.prompt)
        return validate_url(ctx, param, value)


class DefaultOptionFromManifest(click.Option):
    _value_key = '_default_val'

    def __init__(self, *args, **kwargs):
        # https://stackoverflow.com/questions/51846634/click-dynamic-defaults-for-prompts-based-on-other-options
        self.manifest_key = kwargs.pop('manifest_key', None)
        super(DefaultOptionFromManifest, self).__init__(*args, **kwargs)

    def get_default(self, ctx):
        if not hasattr(self, self._value_key):
            manifestfile = ctx.params["manifestfile"]
            manifestjson = get_file_data(manifestfile)
            appManifestDict = json.loads(manifestjson)
            key = self.manifest_key if self.manifest_key else self.name
            value = appManifestDict[key]
            if key == "categories":
                value = list(map(lambda cname: reverse_category_map[cname], value))
            setattr(self, self._value_key, value)
        return getattr(self, self._value_key)

@manifestcmd.command(help="For creating manifest file")
@click.option('-s', '--source', required=True, type=click.Path(exists=True), help='Set filepath for appjson')
@click.option('-c', '--categories', metavar='<category_id>', is_flag=False, required=True, prompt='\nPlease enter the comma separated numerical value corresponding to the app category name.\n\n{}\n\n'.format(APP_CATEGORY_NUM_CHOICES), type=click.STRING, help='Set app category', callback=validate_choice)
@click.option('-a', '--author', required=True, prompt='\nPlease enter the author name.', help="Set author of the app", default="Sumo Logic")
@click.option('-u', '--helpurl', required=True, prompt='\nPlease enter the help url.', help="Set author of the app", callback=validate_url)
def create_manifest(source, categories, author, helpurl):
    # https://stackoverflow.com/questions/33892793/how-to-supply-multiple-options-with-array-validation

    filepath = click.format_filename(source)
    appjson = get_file_data(filepath)
    appjsondic = json.loads(appjson)
    if (appjsondic.get('type', '') not in ('Folder', 'FolderSyncDefinition')) or ('children' not in appjsondic):
        return cli_logger.error("Please export app folder instead of exporting single dashboard. Refer: https://help.sumologic.com/01Start-Here/Library/Export-and-Import-Content-in-the-Library#export-content-in-the-library for more details")
    am = AppManifest(filepath, categories, author, helpurl)
    manifestfile = filepath.replace(".json", ".manifest.json")
    manifest_exists = os.path.isfile(manifestfile)
    force_create = False
    if manifest_exists:
        force_create = input("Manifest already exists.Do you want to continue y/n: ").lower() in ("y", "yes")
    if not manifest_exists or force_create:
        am.prepAppManifest(not USER.is_partner)
        am.set_source_parameters()
        am.set_manifest_parameters()
        am.outputManifestFile()



@manifestcmd.command(help="For updating manifest file")
@click.option('-s', '--sourcefile', required=True, type=click.Path(exists=True), help='Set filepath for appjson')
@click.option('-m', '--manifestfile', required=True, type=click.Path(exists=True), help='Set filepath for manifest json')
@click.option('-c', '--categories', cls=DefaultOptionFromManifest, metavar='<category_id>', is_flag=False, prompt='\nPlease enter the comma separated numerical value corresponding to the app category name, else enter to continue with the default value\n\n -- :\n{}\n\n'.format(APP_CATEGORY_NUM_CHOICES), type=click.STRING, help='Set app category', callback=validate_choice)
@click.option('-a', '--author', cls=DefaultOptionFromManifest, prompt='\nPlease enter the new author name, else enter to continue with the default value', help="Set author of the app")
@click.option('-u', '--helpurl', cls=DefaultOptionFromManifest, prompt='\nPlease enter the new help url, else enter to continue with the default value', help="Set author of the app", callback=validate_url, manifest_key="helpURL")
def update_manifest(sourcefile, manifestfile, categories, author, helpurl):
    # Todo show old category and make it default
    filepath = click.format_filename(sourcefile)
    am = AppManifest(filepath, categories, author, helpurl)
    am.get_manifest(manifestfile)
    am.set_source_parameters()
    am.set_manifest_parameters()
    am.outputManifestFile()

@six.add_metaclass(ABCMeta)
class BaseSubstitutionStrategy(object):


    def __init__(self):
        op_cli = ProviderFactory.get_provider("onprem")
        self.store = op_cli.get_storage("keyvalue", name='sumoapputils', db_dir="~/sumo", logger=cli_logger)
        self.log = get_logger(__name__, LOG_FILEPATH="/tmp/sumoapptestutils.log",
                              LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"))

        self.app_config_key = None
        self.param_mapping = None
        self.reverse_param_mapping = None
        self.appended_params = set()

    @abstractmethod
    def set_source_parameters(self):
        raise NotImplementedError()

    @abstractmethod
    def replace_param_callback(self, query_string, location_text, query_type):
        raise NotImplementedError()

    def _createParameter(self, paramName, paramDataSourceType):
        return {
            "parameterType": "DATA_SOURCE",
            "parameterId": paramName.replace("$$", ""),
            "dataSourceType": paramDataSourceType,
            "label": "%s data source" % paramDataSourceType,
            "description": "%s data source" % paramDataSourceType,
            "example": None
        }

    @classmethod
    def _process_dashboard_queries(cls, dash, callback):
        if TestApp.is_mew_board(dash):
            panels = dash["rootPanel"].get("panels", []) if dash.get("rootPanel") else dash.get("panels", [])
            for panel in panels:
                if panel.get("panelType") in ("TextPanel", "EventsOfInterestScatterPanel") or panel.get("Type") == "TextPanel":
                    continue
                for query in panel["queries"]:
                    panel_name = panel.get("title")
                    if query["queryType"] == "Logs":
                        query["queryString"] = callback(query["queryString"], "Panel: %s" % panel_name, "Logs")
                    else:
                        query["queryString"] = callback(query["queryString"], "Panel: %s" % panel_name, "Metrics")

            variables = dash["rootPanel"].get("variables", []) if dash.get("rootPanel") else dash.get("variables", [])

            for variable in variables:
                var_name = variable.get("name")
                definition = variable.get("sourceDefinition", {})
                if definition.get("variableSourceType", "") == "LogQueryVariableSourceDefinition":
                    definition["query"] = callback(definition["query"], "Variable: %s" % var_name, "Logs")
                elif definition.get("variableSourceType", "") == "MetadataVariableSourceDefinition":
                    definition["filter"] = callback(definition["filter"], "Variable: %s" % var_name, "Metrics")

        else:
            for panel in dash["panels"]:
                if panel["viewerType"] in ("title", "text"):
                    continue
                panel_name = panel.get("name")
                if (panel["queryString"] != ""):
                    panel["queryString"] = callback(panel["queryString"], "Panel: %s" % panel_name, "Logs")
                else:
                    for mquery in panel["metricsQueries"]:
                        mquery["query"] = callback(mquery["query"], "Panel: %s" % panel_name, "Metrics")

    @classmethod
    def _processs_saved_search_queries(cls, search, callback):
        if "searchQuery" in search:
            search["searchQuery"] = callback(search["searchQuery"], "SavedSearch: %s" % search['name'], "Logs")
        else:
            search['search']["queryText"] = callback(search['search']["queryText"], "SavedSearch: %s" % search['name'], "Logs")
            if "viewStartTime" in search["search"]:
                search["search"]["viewStartTime"] = None

    @classmethod
    def process_queries(cls, folder, callback):
        for dash in folder["children"]:
            if dash["type"] in ("Report", "Dashboard", "DashboardSyncDefinition", "MewboardSyncDefinition", "DashboardV2SyncDefinition"):
                cls._process_dashboard_queries(dash, callback)
            elif dash["type"] in ("Search", "SavedSearchWithScheduleSyncDefinition"):
                cls._processs_saved_search_queries(dash, callback)
            elif dash["type"] in ("Folder", "FolderSyncDefinition"):
                cls.process_queries(dash, callback)


class WholePrefixParameterSubstitutionMixin(BaseSubstitutionStrategy):

    source_category_regex = r'\b(?P<expr>(?:_sourceCategory)\s*=\s*(?:\"[\w\*\-\/\s]+\"|[\w\*\-\/]+))'
    metric_param = "metricsrc"
    log_param = "logsrc"

    def _get_substition_expressions(self, queryString, regex):
        matched_params = re.findall(regex, queryString, flags=re.IGNORECASE)

        substitution_expr = set()
        for param in matched_params:
            param = param.strip()
            param = re.escape(param)
            expr = param.replace("\\ ", "\s*")
            substitution_expr.add(expr)
            self.log.debug("After replacement with regex: %s result: %s" % (expr, re.sub(expr, "$$logparam ", queryString[: 100], flags=re.I)))

        return substitution_expr

    def _get_param_name(self, text, mapping):

        num=0
        param_name = "%s%s" % (text, "" if num == 0 else num)
        while (param_name in mapping):
            num += 1
            param_name = "%s%s" % (text, "" if num == 0 else num)

        return param_name

    def replace_param_callback(self, query_string, location_text, query_type):
        self.log.debug("CHECKING %s" % location_text)
        # case if space commes first
        # if \s* comes first

        with_sc = self._get_substition_expressions(query_string, self.source_category_regex)
        for expr in with_sc:
            unique_expr = expr.replace("\s*", "").lower()
            if expr in self.reverse_param_mapping:
                param_name = self.reverse_param_mapping[expr]
                query_string = re.sub(expr, "$$%s " % param_name, query_string, flags=re.IGNORECASE)
            else:
                if unique_expr in self.reverse_param_mapping:
                    param_name = self.reverse_param_mapping[unique_expr]
                else:
                    param_name = self._get_param_name(self.log_param if query_type == "Logs" else self.metric_param, self.param_mapping)
                    self.log.debug("found new params %s" % expr)
                    self.param_mapping[param_name] = [unique_expr]
                    self.reverse_param_mapping[unique_expr] = param_name

                if expr not in self.param_mapping[param_name]:
                    self.param_mapping[param_name].append(expr)
                self.reverse_param_mapping[expr] = param_name
                query_string = re.sub(expr, "$$%s " % param_name, query_string, flags=re.IGNORECASE)
            self.appended_params.add(param_name)

        # existing params
        return query_string

    def set_source_parameters(self):
        self.appManifestDict["parameters"] = []
        self.process_queries(self.appDict, self.replace_param_callback)

        self.appjson = json.dumps(self.appDict, indent=4)
        without_sc_for_jsonstr = r'(?P<expr>(?:_source|_sourceName|_sourceHost|_collector|_sourceCategory)\s*=\s*(?:\\"[\w\*\-\s\/]+\\"|[\w\*\-\/]+)(?:(?i:\s+OR\s+|\s+AND\s+)(?:_source|_sourceName|_sourceHost|_collector|_sourceCategory)\s*=\s*(?:\\"[\w\*\-\/\s]+\\"|[\w\*\-\/]+))*)'
        without_sc_expr = set([e.replace('\s*', " ") for e in
                               re.findall(without_sc_for_jsonstr, self.appjson, flags=re.IGNORECASE)])

        if len(without_sc_expr) > 0:
            self.log.error("Following metadata is not recommended in queries. For best practices on building queries follow this doc https://docs.google.com/document/d/1xfYfruru0RFWOH23GRrRzosSlepJUTcakLFHLHdpEtc/edit#heading=h.62uucfpoixq2. Once fixed, please rerun this command\n %s" % "\n".join(without_sc_expr))

        new_param_mapping = {}
        for param_name, expr_list in self.param_mapping.items():
            if param_name in self.appended_params or param_name in self.appjson:
                param_type = "LOG" if param_name.startswith(self.log_param) else "METRICS"
                # saves mapping
                self.appManifestDict["parameters"].append(self._createParameter(param_name, param_type))
                new_param_mapping[param_name] = expr_list

        self.current_app_config["param_mapping"] = new_param_mapping
        self.app_config[self.app_config_key] = self.current_app_config
        self.store.set("app_config", self.app_config)

    def test_substitution(self):

        self._get_substition_expressions(
            '(_source="kaudit-data*" AND not !_collector="Kaudit Collector") and _sourcecategory="detections" Or _sourcename=labs/aws* mykeywords| json', self.source_category_regex)

        self._get_substition_expressions(
            '_source="kaudit-data" and not _collector="KauditCollector" and  _sourcecategory="detections" kw1 kw2| json', self.source_category_regex)

        self._get_substition_expressions(
            '(_source="kaudit-data" and not _collector="KauditCollector") and  _sourcecategory="detections" | json', self.source_category_regex)

        self._get_substition_expressions(
            'not ( _source="kaudit-data" and _collector="KauditCollector" ) OR  _sourcecategory="detections" | json', self.source_category_regex)

        self._get_substition_expressions('( not _source="kaudit-data" and _collector="KauditCollector" ) OR  _sourcecategory="detections" | json', self.source_category_regex)


class AppManifest(WholePrefixParameterSubstitutionMixin):

    MANDATORY_CATEGORY_FOR_PARTNER_APPS = "Sumo Logic Certified"

    def __init__(self, filepath, categories, author, help_url):
        super(AppManifest, self).__init__()
        # cfg = Config()
        # root_dir = os.path.dirname(os.path.abspath(__file__))
        # base_config_path = os.path.join(root_dir, "metadata.yaml")
        # self.base_config = cfg.read_config(base_config_path)
        self.appjson = get_file_data(filepath)
        self.author = author
        self.help_url = help_url
        self.sourceFilePath = filepath
        self.app_config_key = get_app_config_key(filepath)
        self.categories = categories
        if USER.is_partner and self.MANDATORY_CATEGORY_FOR_PARTNER_APPS not in self.categories:
            self.categories.append(self.MANDATORY_CATEGORY_FOR_PARTNER_APPS)
        self.appDict = json.loads(self.appjson)
        dashboard_class = get_test_class(appjson=self.appDict)
        dashboards, searches = dashboard_class.get_content(self.appDict)
        self.log_queries, self.metric_queries = dashboard_class.extract_queries(dashboards)
        self.saved_search_queries = dashboard_class.get_saved_search_queries(searches)
        self.app_config = self.store.get("app_config", {})
        self.current_app_config = self.app_config.get(self.app_config_key, {})
        self.param_mapping = self.current_app_config.get("param_mapping", {})  # param name - expr
        self.reverse_param_mapping = {}
        for param, expr_list in self.param_mapping.items():
            for expr in expr_list:
                self.reverse_param_mapping[expr] = param


    def prepAppManifest(self, generate_uuid):
        self.appManifestDict = {
            "name": self.appDict["name"].strip(),
            "description": self.appDict["description"].strip(),
            "version": "1.0",
            "manifestVersion": "0.1",
            "helpURL": "https://help.sumologic.com/?cid=xxxx",
            "hoverText": None,
            "iconURL": "https://s3.amazonaws.com/app_icons/SumoLogic.png",
            "screenshotURLs": [],
            "preview": False,
            "communityURL": "https://support.sumologic.com/hc/en-us/community/topics/200263058-Applications-and-Integrations",
            "requirements": [],
            "requiresInstallationInstructions": False,
            "installationInstructions": None,
            'categories': self.categories,
            "parameters": []
        }
        if generate_uuid:
            self.appManifestDict["uuid"] = str(uuid.uuid4())


    def outputManifestFile(self):
        prettyJsonOutput = json.dumps(self.appManifestDict, sort_keys=True, indent=4, separators=(',', ': '))
        manifestFilePath = self.sourceFilePath.replace(".json", ".manifest.json")
        with open(manifestFilePath, 'w') as f:
            f.write(prettyJsonOutput)
        with open(self.sourceFilePath, 'w') as f:
            f.write(self.appjson)
        self.log.info("Manifest file has been generated: %s. You can open and review it." % manifestFilePath)

    def get_manifest(self, filepath):
        manifestjson = get_file_data(filepath)
        self.appManifestDict = json.loads(manifestjson)


    def set_manifest_parameters(self):
        manifest_key_mapping = {"help_url": "helpURL"}
        for param in ["categories", "author", "help_url"]:
            new_val = getattr(self, param, None)
            if new_val:
                self.appManifestDict[manifest_key_mapping.get(param, param)] = new_val