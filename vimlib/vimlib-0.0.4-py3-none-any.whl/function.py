import vim


class Function:
    def __init__(
        self,
        name,
        arguments=None,
        optional_arguments=None,
        overwrite=True,
    ):
        # ADD optional_arguments - ...
        # ADD <f-args>
        # ADD <q-args>

        self.name = name
        if not arguments:
            self.arguments = []
        else:
            # FIX: arg1, arg2, optarg1=value, ...
            self.arguments = arguments
        if not optional_arguments:
            self.optional_arguments = []
        else:
            # FIX: arg1, arg2, optarg1=value, ...
            self.optional_arguments = optional_arguments

        bang = '!' if overwrite else ''

        # FIX - Spacing to the left
        command = f"""function{bang} {self.name}({arguments})


        """.strip()
        vim.command(command)
