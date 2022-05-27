import json
import os
import shutil

import click
import msal
import requests
from time import sleep

from arcl.config import (
    get_config_path,
    get_api_config,
    get_legacy_config_path,
    get_legacy_token_path,
    get_token_path,
    ARCHIMEDES_CONF_DIR,
)
from arcl.token_cache import get_token_cache

AUTH_ACTIONS_LOGIN = "login"
AUTH_ACTIONS_LOGOUT = "logout"
AUTH_ACTIONS_GET_TOKEN = "get-token"
AUTH_ACTIONS_SHOW = "show"
AUTH_ACTIONS = [
    AUTH_ACTIONS_LOGIN,
    AUTH_ACTIONS_LOGOUT,
    AUTH_ACTIONS_GET_TOKEN,
    AUTH_ACTIONS_SHOW,
]


def get_accepted_env():
    for _ in range(0, 10):
        try:
            response = requests.get(
                "https://arclconfig.azureedge.net/config.json"
            ).json()
            return tuple(response.keys())
        except:
            sleep(3)
    raise Exception("Unable to get config from arclconfig.")


class ArchimedesAuth:
    def __init__(self, env):
        self.env = env
        self.saved_config_path = get_config_path(env)
        self.token_path = get_token_path(env)
        self.api_config = get_api_config(self.env)
        self.app = self.build_msal_app(
            self.api_config.client_id, cache=get_token_cache(env)
        )

    def get_scopes(self):
        return [
            f"api://{self.api_config.aad_app_client_id}/.default",
        ]

    def get_token_expiry(self):
        accounts = self.app.get_accounts()
        if not accounts:
            return None

        chosen = accounts[0]
        result = self.app.acquire_token_silent(self.get_scopes(), account=chosen)
        return result["expires_in"]

    def get_access_token_silent(self):
        # We now check the cache to see
        # whether we already have some accounts that the end user already used to sign in before.
        accounts = self.app.get_accounts()
        if not accounts:
            return None

        chosen = accounts[0]
        result = self.app.acquire_token_silent(self.get_scopes(), account=chosen)

        if result is None or "access_token" not in result:
            click.echo("Could not get access token silently")

            if result is not None:
                click.echo(result.get("error"))
                click.echo(result.get("error_description"))

            return None

        return result.get("access_token")

    def get_access_token_by_device_flow(self):
        flow = self.app.initiate_device_flow(self.get_scopes())
        message = flow.get("message")
        click.echo(message)
        result = self.app.acquire_token_by_device_flow(flow)

        if result is None or "access_token" not in result:
            click.echo("Could not login. Try logging out and logging in again.")

            if result is not None:
                click.echo(result.get("error"))
                click.echo(result.get("error_description"))

            return None

        return result.get("access_token")

    def get_access_token(self):
        access_token = self.get_access_token_silent()
        if not access_token:
            access_token = self.get_access_token_by_device_flow()
        return access_token

    def login(self, organization_id):
        access_token = self.get_access_token()

        if organization_id is None:
            url = f"{self.api_config.url}/v2/config/"
        else:
            url = f"{self.api_config.url}/v1/config/{organization_id}/"

        try:
            page = requests.get(
                url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
            )
            page.raise_for_status()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            click.echo("Failed connecting to the server", e)
        except requests.exceptions.HTTPError:
            click.echo(page.content)
            contents = page.json()
            if "detail" in contents:
                click.echo(contents["detail"])
            else:
                click.echo(contents)
        else:
            config = page.json()
            config_json = json.dumps(config, indent=2)
            open(self.saved_config_path, "w").write(config_json)
            click.echo(f"Login successful into env: {self.env}")

            # copy jsona and msal to default files for backward compatibility
            shutil.copy(self.saved_config_path, get_legacy_config_path())
            shutil.copy(self.token_path, get_legacy_token_path())

    @staticmethod
    def show():
        all_env_details = {}
        for env in get_accepted_env():
            saved_config_path = get_config_path(env)
            if not os.path.exists(saved_config_path):
                continue
            with open(saved_config_path, "r") as file:
                config = json.load(file)
            all_env_details[env] = config["user"]

        if not len(all_env_details):
            click.echo("No accounts logged in.")
            return
        click.echo("Details of all accounts are below.")
        sep = "   "
        dp_color = "blue"
        for env, config in all_env_details.items():
            click.echo("")
            click.echo(sep + click.style("ENVIRONMENT:", fg=dp_color) + f"{env}")
            click.echo(
                sep * 2 + click.style("Name:", fg=dp_color) + f" {config['name']}"
            )
            click.echo(
                sep * 2
                + click.style("Username:", fg=dp_color)
                + f" {config['username']}"
            )
            click.echo(
                sep * 2 + click.style("Email:", fg=dp_color) + f" {config['email']}"
            )
            app = ArchimedesAuth(env)
            click.echo(
                sep * 2
                + click.style("Token expires in:", fg=dp_color)
                + f" {app.get_token_expiry()} seconds"
            )

    def logout(self):
        # remove older tokens created on previous versions
        for file_to_remove in (
            "arcl.json",
            "msal.cache.bin",
        ):
            try:
                os.remove(os.path.join(ARCHIMEDES_CONF_DIR, file_to_remove))
            except FileNotFoundError:
                pass

        if os.path.exists(self.saved_config_path):
            os.remove(self.saved_config_path)

        if os.path.exists(self.token_path):
            os.remove(self.token_path)

        click.echo(f"Logout successful from  env: {self.env}")

    def build_msal_app(self, client_id, cache=None):
        return msal.PublicClientApplication(
            client_id,
            authority=self.api_config.authority,
            token_cache=cache,
        )
