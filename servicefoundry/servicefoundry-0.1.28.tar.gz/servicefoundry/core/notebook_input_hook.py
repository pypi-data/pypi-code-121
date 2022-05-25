from servicefoundry.internal.clients.service_foundry_client import (
    ServiceFoundryServiceClient,
)
from servicefoundry.internal.template.input_hook import InputHook


class NotebookInputHook(InputHook):
    def __init__(self, tfs_client: ServiceFoundryServiceClient):
        super().__init__(tfs_client)

    def ask_string(self, param):
        return questionary.text(param.prompt, default=param.default).ask()

    def ask_number(self, param):
        while True:
            value = questionary.text(param.prompt, default=str(param.default)).ask()
            if value.isdigit():
                return int(value)
            else:
                print("Not an integer Value. Try again")

    def ask_option(self, param):
        return questionary.select(param.prompt, choices=param.options).ask()

    def ask_workspace(self, param):
        space_choices = self.get_space_choices()
        space_choices.append(
            Choice(title=MSG_CREATE_NEW_SPACE, value=MSG_CREATE_NEW_SPACE)
        )
        space = questionary.select(param.prompt, choices=space_choices).ask()

        if space == MSG_CREATE_NEW_SPACE:
            cluster = tfs_client.session.get_cluster()
            if not cluster:
                raise Exception(
                    "No default cluster set to create workspace. "
                    "Use `sfy use cluster` to pick and set a default cluster"
                )
            new_space_name = questionary.text(
                "Please provide a name for your workspace"
            ).ask()
            response = tfs_client.create_workspace(
                cluster_id=cluster["id"], name=new_space_name
            )
            console.print("Please wait while your workspace is being created. ")
            tfs_client.tail_logs(runId=response["runId"], wait=True)
            console.print(f"Done, created new workspace with name {new_space_name!r}")
            space = response["workspace"]

        return space["fqn"]
