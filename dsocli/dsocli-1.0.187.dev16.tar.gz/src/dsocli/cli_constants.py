CLI_COMMANDS_HELP = {
    'parameter': {
        'add': """Add a parameter to a context, or update a parameter if it is already existing in the context.\n
                ** Tips: 1) If the parameter is inherited from the parent contexts, it will be overriden in the context. 2) Multiple parameters may be added at once using the '--input' option.\n
                KEY: The identifier of the parameter to be added. It may also be provided using the '--key' option.\n
                VALUE: The value for the parameter. If the parameter is already existing in the context, the value will be updated to the new one. It may also be provided using the '--value' option.\n
                """,
        'list': """Return the list of owned/inherited parameters in a context.\n
                ** Tips: 1) To limit the list to the owned/overriden parameters only, use the '--uninherited' option. This will return only the context specific parameters.
                """,
        'get': """Return the current value of a parameter.\n
                ** Tips: 1) The parameter may be inherited from the parent contexts or owned by the given context.\n
                KEY: The identifier of the parameter. It may also be provided using the '--key' option.\n
                """,
        'edit': """Edit the current value of a parameter.\n
                ** Tips: 1) The parameter must be owned by the given context.\n
                KEY: The identifier of the parameter. It may also be provided using the '--key' option.\n
                """,
        'delete': """Delete a parameter from a context.\n
                ** Tips: 1) The inherited parameters cannot be deleted. The context must be the owner of the parameter or a not found error will be returned. 2) Multiple parameters may be deleted at once using the '--input' option.\n         
                KEY: The identifier of the parameter to be deleted. It may also be provided using the '--key' option.\n
                """,
        'history': """Return the revision history of parameter.\n
                ** Tips: 1) The parameter may be inherited from the parent contexts or owned by the given context.\n
                KEY: The identifier of the parameter. It may also be provided using the '--key' option.\n
                """,
    },
    'secret': {
        'add': """Add a secret to a context, or update a secret if it is already existing in the context.\n
                ** Tips: 1) If the secret is inherited from the parent contexts, it will be overriden in the context. 2) Multiple secrets may be added at once using the '--input' option.\n
                KEY: The identifier of the secret to be added. It may also be provided using the '--key' option.\n
                VALUE: The value for the secret. If the secret is already existing in the context, the value will be updated to the new one. It may also be provided using the '--value' option.\n
                """,
        'list': """Return the list of owned/inherited secrets in a context.\n
                ** Tips: 1) To limit the list to the owned/overriden secrets only, use the '--uninherited' option. This will return only the context specific secrets.
                """,
        'get': """Return the current value of a secret.\n
                ** Tips: 1) The secret may be inherited from the parent contexts or owned by the given context.\n
                KEY: The identifier of the secret. It may also be provided using the '--key' option.\n
                """,
        'edit': """Edit the current value of a secret.\n
                ** Tips: 1) The secret must be owned by the given context.\n
                KEY: The identifier of the secret. It may also be provided using the '--key' option.\n
                """,
        'delete': """Delete a secret from a context.\n
                ** Tips: 1) The inherited secrets cannot be deleted. The context must be the owner of the secret or a not found error will be returned. 2) Multiple secrets may be deleted at once using the '--input' option.\n         
                KEY: The identifier of the secret to be deleted. It may also be provided using the '--key' option.\n
                """,
        'history': """Return the revision history of secret.\n
                ** Tips: 1) The secret may be inherited from the parent contexts or owned by the given context.\n
                KEY: The identifier of the secret. It may also be provided using the '--key' option.\n
                """,
    },
    'template': {
        'add': """Add a template to a context, or update the contents if it is already existing in the context.\n
                ** Tips: 1) If the template is inherited from the parent contexts, it will be overriden in the context. 2) Multiple templates may be added recursively from a directory.\n
                KEY: The identifier of the template to be added. It may also be provided using the '--key' option.\n
                """,
        'list': """Return the list of templates in a context.\n
                ** Tips: 1) To limit the list to the owned/overriden templates only, use the '--uninherited' option. This will return only the context specific templates.
                """,
        'get': """Return the contents of a template.\n
                ** Tips: 1) The template may be inherited from the parent contexts or owned by the given context.\n
                KEY: The identifier of the secret. It may also be provided using the '--key' option.\n
                """,
        'edit': """Edit the contents of a template.\n
                ** Tips: 1) The template must be owned by the given context.\n
                KEY: The identifier of the secret. It may also be provided using the '--key' option.\n
                """,
        'delete': """Delete a template from a context.\n
                ** Tips: 1) The inherited template cannot be deleted. The context must be the owner of the secret or a not found error will be returned. 2) Multiple templates may be deleted at once using the '--input' option.\n
                KEY: The identifier of the template to be deleted. It may also be provided using the '--key' option.\n
                """,
        'history': """Return the revision history of template.\n
                ** Tips: 1) The template may be inherited from the parent contexts or owned by the given context.\n
                KEY: The identifier of the template. It may also be provided using the '--key' option.\n
                """,
        'render': """Render templates in a context.\n
                    """,
    },
    'config': {
        'list': """Return the list of configuration settings in a context.\n
                ** Tips: 1) To limit the list to the owned/overriden configuration settings only, use the '--uninherited' option. This will return only the context specific configuration settings.
                """,
        'get': """Get DSO application configuration.\n
                ** Tips: 1) Use --local or --global to get local or global configuration only.\n
                KEY: The key of the configuration
                """,
        'add': """Add DSO application configuration.\n
                ** Tips: 1) Use --local or --global to get local or global configuration only.\n
                KEY: The key of the configuration. It may also be provided using the '--key' option.\n
                VALUE: The value for the configuration. It may also be provided using the '--value' option.\n
                """,
        'delete': """Delete DSO application configuration.\n
                ** Tips: 1) Use --local or --global to get local or global configuration only.\n
                KEY: The key of the configuration
                """,
        'init': """Initialize DSO configuration for the working directory.\n
                ** Tips: 1) Use --input to load connfiguration from a file.\n
                The option '--working-dir' can be used to specify a different working directory than the current directory where dso is running in.\n
                """,
        'edit': """Edit the current value of a configuration setting.\n
                ** Tips: 1) The setting must be owned by the given context.\n
                KEY: The identifier of the secret. It may also be provided using the '--key' option.\n
                """,
      },
    'package': {
        'build': """Build a distrubutabkle package, and adds it to artifact store.\n
                ** Tips: 1) ... 2) ...\n
                """,
        'list': """Return the list of packages in a context.\n
                ** Tips: 1) To limit the list to the owned/overriden packages only, use the '--uninherited' option. This will return only the context specific packages.
                """,
        'get': """Get a package from artifact store.\n
                ** Tips: 1) ... 2) ...\n
                KEY: The identifier of the package. It may also be provided using the '--key' option.\n
                """,
        'delete': """Delete a package from a context.\n
                ** Tips: 1) The inherited package cannot be deleted. The context must be the owner of the secret or a not found error will be returned. 2) Multiple packages may be deleted at once using the '--input' option.\n
                KEY: The identifier of the package to be deleted. It may also be provided using the '--key' option.\n
                """,
    },
    'release': {
        'create': """Create a deployment release, and adds it to artifact store.\n
                ** Tips: 1) ... 2) ...\n
                """,
        'list': """Return the list of releases in a context.\n
                ** Tips: 1) To limit the list to the owned/overriden releases only, use the '--uninherited' option. This will return only the context specific releases.
                """,
        'get': """Get a release from artifact store.\n
                ** Tips: 1) ... 2) ...\n
                KEY: The identifier of the release. It may also be provided using the '--key' option.\n
                """,
        'delete': """Delete a release from a context.\n
                ** Tips: 1) The inherited release cannot be deleted. The context must be the owner of the secret or a not found error will be returned. 2) Multiple releases may be deleted at once using the '--input' option.\n
                KEY: The identifier of the release to be deleted. It may also be provided using the '--key' option.\n
                """,
    },
    'network': {
        'subnet': """Get subnet plan layout of the applcation.\n
                """,
    },
}

CLI_COMMANDS_SHORT_HELP = {
    'version': "Display versions.",
    'parameter': {
        'list': "List parameters available to the application.",
        'add': "Add/Update one or multiple parameters to the application.",
        'get': "Get the value of a parameter.",
        'edit': "Edit the value of a parameter.",
        'delete': "Delete one or multiple parameters from the application.",
        'history': "Get the revision history of a parameter.",
    },
    'secret': {
        'list': "List secrets available to the application.",
        'add': "Add/Update one or multiple secrets to the application.",
        'get': "Get the value of a secret.",
        'edit': "Edit the value of a secret.",
        'delete': "Delete one or multiple secrets from the application.",
        'history': "Get the revision history of a secret.",
    },
    'template': {
        'list': "List templates available to the application.",
        'add': "Add/Update a template to the application.",
        'get': "Get the contents of a template.",
        'edit': "Edit the contents of a template.",
        'delete': "Delete one or multiple templates from the application.",
        'history': "Get the revision history of a template.",
        'render': "Render templates using parameters and secrets in a context.",
    },
    'package': {
        'list': "List packages built for the application available on arctifact store.",
        'build': "Build a distributable package for the application.",
        'get': "Download a build package from arctifact store.",
        'delete': "Delete a build package from arctifact store.",
    },
    'release': {
        'list': "List deployment releases for the application.",
        'create': "Create a deployment release for the application.",
        'get': "Download an application deployment release.",
        'delete': "Delete a deployment release from the application.",
    },
    'config': {
        'list': "List configuration settings available to the application.",
        'get': "Get DSO application configuration.",
        'add': "Add DSO application configuration.",
        'delete': "Delete a DSO application configuration.",
        'init': "Initialize DSO application in the working directory.",
        'edit': "Edit the value of a configuration setting.",
    },
    'network': {
        'subnet': "Get subnet plan layout of the application.",
    }
}
CLI_PARAMETERS_HELP = {
    'common': {
        'working_dir': "Path to a (local) directory where the DSO application configuration resides. By default, the current working directory will be used if the option is not provided.",
        'verbosity' : "Specifies the logging verbosity, where 0 is for logging critical fatal errors only, 1 also logs error messages, 2 also logs warnings, 3 also logs information messages, 4 also logs debug messages, and finally 5 logs everything.",
        'stage' : "Target a specific stage using the stage identifier, which is combination of a name and an optional number, where name must conform to ^([a-zA-Z][a-zA-Z0-9]+)$ regex expression. If no /<number> is specified, the default environment (/0) in the given context will be target.",
        'input' : "Path to a (local) file defining the input data. Use '-' to read from the shell pipe or stdin. Use '--format' to specify the format if needed.",
        'format': "Specifies the format of the output or the input if mixed with the '--input' option.",
        'config': "Comma separated list of key/value pairs to temporarily override the current DSO application configuration. It takes effect only while executing the command and does not have any lasting effect on the DSO application configuration or subsequent command executions.",
        'query': "Customize output using JMESPath query language.",
        'query_all': "Include all the available fields in the ouput.",
        'global_scope': "Use the global scope.",
        'namespace_scope': "Use the namespace scope.",
        'filter': "Use a regex pattern to filter result by the provider.",
        'context': "Specifies the context to be used.",
    },
    'parameter': {
        'key': "The key of the parameter. See KEY argument for more details.",
        'value': "The value for the parameter. See VALUE argument for more details.",
        'query_values': "Include parameter values in the output.",
        'uninherited': "Select only parameters which are specific to the gievn context, i.e. not inherited from the parent contexts.",
        'revision': "The revision ID whose value to be fetched.",
    },
    'secret': {
        'key': "The key of the secret",
        'value': "The value for the secret",
        'decrypt': "Decrypt the secret value.",
        'query_values': "Include secret values in the output.",
        'uninherited': "Select only secrets which are specific to the gievn context, i.e. not inherited from the parent contexts.",
        'revision': "The revision ID whose value to be fetched.",
        'ask_password': "Inputing password from stdin.",
    },
    'template': {
        'type': "Type of the template. Use 'resource' for templates needed at the provision time when provisioning resources required by the application to run such as SQS queus, SNS topics, and CI/CD piplines.\nUse 'package' for templates needed at the build time when generating a package.\nUse 'release' for templates needed at the deploy time when generating a release." ,
        'key': "The key of the template",
        'limit': "Limit templates to be rendered.",
        'render_path': "Path (relative to the root of the DSO application) where rendered template will be placed at.",
        'query_render_path': "Include the template render paths in the output.",
        'contents_path' : "Path to a local file or directory containing the template contents.",
        'recursive' : "Add files recursively.",
        'uninherited': "Select only templates which are specific to the gievn context, i.e. not inherited from the parent contexts.",
        'include_contents': "Include template contenets in the output.",
        'rendered': "Specifies whether render or raw contents.",
    },
    'config': {
        'key': "The key of the configuration setting",
        'value': 'Value for the configuration setting',
        'input' : "Path to a local (yaml) file inputing the configuration. Use '-' to read from the shell pipe or stdin.",
        'rendered': "Whether or not render configuration settings.",
        'override_inherited': "Explicitly override inherited configuration locally.",
        'setup': "Run a setup wizard to assist configuring the DSO application.",
        'uninherited': "Select only condifuration settings which are specific to the gievn context, i.e. not inherited from the parent contexts.",
        'local': "Use local configuration only.",
        'remote': "Use remote configuration only via config service.",
        'revision': "The revision ID whose value to be fetched.",

    },
    'package': {
        'key': "The key of the package. See KEY argument for more details.",
    },
    'release': {
        'key': "The key of the release. See KEY argument for more details.",
    },
    'network': {
        'subnet_layout_mode': "Select the subnet plan layout mode.",
    },

}


CLI_MESSAGES = {
    'MissingOption': "Missing option {0}.",
    'MissingArgument': "Missing argument {0}.",
    'ArgumentProvided': "The following argument/option must be provided: {0}",
    'ArgumentsOnlyOneProvided': "Only one of the following arguments/options may be provided: {0}",
    'ArgumentsAtLeastOneProvided': "At least one of the following arguments/options must be provided: {0}",
    'ArgumentsAllProvided': "All of the following arguments/options must be provided: {0}",
    'ArgumentsNoneProvided': "The following arguments/options cannot be provided: {0}",
    'ArgumentsNotAllProvided': "The following arguments/options cannot be provided together: {0}",
    'ArgumentsProvidedBecause': "Since {0} provided, the following argument/option must also be provide: {1}",
    'ArgumentsOnlyOneProvidedBecause': "Since {0} provided, only one of the following arguments/options may be provided: {1}",
    'ArgumentsAtLeastOneProvidedBecause': "Since {0} provided, at least one of the following arguments/options must also be provided: {1}",
    'ArgumentsAllProvidedBecause': "Since {0} provided, all of the following arguments/options must also be provide: {1}",
    'ArgumentsNoneProvidedBecause': "Since {0} provided, the following arguments/options cannot be provided: {1}",
    'ArgumentsNotAllProvidedBecasue': "Since {0} provided, the following arguments/options may be provided together: {1}",
    'TryHelpWithCommand': "Try '{0} --help' for more details.",
    'TryHelp': "Try the command with '-h' / '--help' option for more details.",
    'InvalidFileFormat': "Invalid file, not conforming to the expected '{0}' format.",
    'EnteredSecretValuesNotMatched': "Entered values for the secret did not macth.",
    'RenderPathNotReleative': "Render path '{0}' is not releative to the application root directory.",
    # 'InvalidRenderPath': "'{0}' is not a valid render path.",
#     'InvalidRenderPathExistingDir': "'{0}' is not a valid render path because it is an existing directory.",
    'InvalidFilter': "Invalid regex pattern for filter: {0}",
    'NoChanegeDetectedAfterEditing': "Edit canceled, no change detected after editing.",
    'ParameterNotFound': "Parameter '{0}' not found in the given context: namespace={1}, application={2}, stage={3}, scope={4}",
    'SecretNotFound': "Secret '{0}' not found in the given context: namespace={1}, application={2}, stage={3}, scope={4}",
    'TemplateNotFound': "Template '{0}' not found in the given context: namespace={1}, application={2}, stage={3}, scope={4}",
    'MissingField': "Missing field: {0}",
}
