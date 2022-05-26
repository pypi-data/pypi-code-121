TOOL_NAME = NAMESPACE = 'boip'

CONSOLE_SCRIPTS = [
    f'{TOOL_NAME} = botoolkit.bo_ip.main:main',
]

NAMESPACES = {
    f'{NAMESPACE}': [
        'ping = botoolkit.bo_ip.commands:BOIPPingCommand',
    ],
}
