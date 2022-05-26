SFY = "sfy"

# TODO: probably create another `rich_messages.py` and apply all formatting there
PROMPT_LOGIN_SUCCESSFUL = f"""[green bold]Login Successful![/]"""
PROMPT_LOGIN_INFO = (
    f"""[yellow]You are logged in as {{username!r}} with email {{email!r}}[/]"""
)
PROMPT_LOGOUT_SUCCESSFUL = f"""[green bold]Logged Out![/]"""
PROMPT_POST_LOGIN = (
    f"""[yellow]You can now initiate a new service using [bold]{SFY} init[/][/]"""
)
PROMPT_ALREADY_LOGGED_OUT = f"""[yellow]You are already logged out[/]"""
PROMPT_SETTING_CLUSTER_CONTEXT = f"""[yellow]Setting cluster {{!r}} as default[/]"""
PROMPT_SETTING_WORKSPACE_CONTEXT = f"""[yellow]Setting workspace {{!r}} as default[/]"""
PROMPT_UNSETTING_WORKSPACE_CONTEXT = (
    f"""[yellow]Removing workspace {{!r}} as default[/]"""
)
PROMPT_USING_CLUSTER_CONTEXT = f"""[yellow]Using cluster {{!r}}[/]"""
PROMPT_USING_WORKSPACE_CONTEXT = f"""[yellow]Using workspace {{!r}}[/]"""
PROMPT_CREATING_NEW_WORKSPACE = f"""[yellow]Creating a new workspace {{!r}}[/]"""
PROMPT_REMOVING_WORKSPACE = f"""[yellow]Removing workspace {{!r}}[/]"""
PROMPT_REMOVING_SERVICE = f"""[yellow]Removing service {{!r}}[/]"""
PROMPT_NO_WORKSPACES = f"""[yellow]No workspaces found. You can create one with [bold]{SFY} create workspace[/][/]"""
PROMPT_NO_SERVICES = f"""[yellow]No services found. You can create one with [bold]{SFY} init[/] and then
deploy it using [bold]{SFY} deploy[/][/]"""
PROMPT_NO_DEPLOYMENTS = f"""[yellow]No deployments found. You can create one with [bold]{SFY} deploy .[/] from within
your service folder"""
