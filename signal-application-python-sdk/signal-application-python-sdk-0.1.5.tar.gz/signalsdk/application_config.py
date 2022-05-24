import logging
from datetime import datetime
from signalsdk.signed_request_client import signed_request
from signalsdk.signal_exception import SignalAppParamNotFoundError

Application = {
    "id": "",
    "name": "string",
    "localVersion": "",
    "versionOnGreengrass": "",
    "sdkPubTopic": "",
    "sdkSubTopic": "",
    "settings": []
}

DeploymentInfo = {
    "applications": [],
    "name": "",
    "createdAt": "",
    "deploymentVersion": ""
}

ApplicationConfig = {
    "version": "",
    "createdAt": "",
    "settingsForApp": {},
    "settingsForSDK": {}
}


def get_config_for_app(device_deployment_id,
                       group_deployment_id,
                       account_id,
                       application_id,
                       device_api_dn):
    if not device_deployment_id and not group_deployment_id:
        logging.error("Neither device deployment id nor group deployment id exists")
        raise SignalAppParamNotFoundError("deploymentId and groupDeploymentId")
    app_device_deployment_settings = None
    app_group_deployment_settings = None
    if device_deployment_id:
        logging.info("signalsdk::Retrieving device deployment info...")
        app_device_deployment_settings = get_app_config_for_deployment(
            device_deployment_id, account_id, application_id, device_api_dn)
    if group_deployment_id:
        logging.info("signalsdk::Retrieving group deployment info...")
        app_group_deployment_settings = get_app_config_for_deployment(
            group_deployment_id, account_id, application_id, device_api_dn)
    if not app_device_deployment_settings:
        return app_group_deployment_settings
    if not app_group_deployment_settings:
        return app_device_deployment_settings
    device_deployment_date = datetime.strptime(app_device_deployment_settings["createdAt"])
    group_deployment_date = datetime.strptime(app_group_deployment_settings["createdAt"])
    if device_deployment_date > group_deployment_date:
        return app_device_deployment_settings
    return app_group_deployment_settings

def get_app_config_for_deployment(deployment_id, account_id, application_id, device_api_dn):
    api_path = "".join(["/accounts/", account_id, "/deployments/", deployment_id])
    api_url = format_base_url(device_api_dn + api_path)
    logging.info(f"signalsdk::sending signed request: url: {api_url}")
    deploymentInfo = signed_request(method='GET', url=api_url, data={}, headers={})
    logging.info(f"signalsdk::Deployment Info: {deploymentInfo}")
    app_list = deploymentInfo["applications"]
    final_config = {}
    for app in app_list:
        if app["id"] == application_id:
            applicationInfo = app
    if applicationInfo:
        app_settings = {}
        for item in applicationInfo["settings"]:
            app_settings[item['key']] = item['value']
        final_config = {"createdAt": deploymentInfo["createdAt"],
                        "version": applicationInfo["versionOnGreengrass"],
                        "settingsForSDK": {"sdkPubTopic": applicationInfo["sdkPubTopic"],
                                           "sdkSubTopic": applicationInfo["sdkSubTopic"]},
                        "settingsForApp": app_settings}
    return final_config

def format_base_url(base_url: str):
    if base_url.startswith("https://") or base_url.startswith("http://"):
        return base_url
    return "https://" + base_url
