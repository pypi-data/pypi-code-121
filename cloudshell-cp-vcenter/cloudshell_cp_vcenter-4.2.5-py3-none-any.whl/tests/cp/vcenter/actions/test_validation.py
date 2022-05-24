from cloudshell.cp.vcenter.actions.validation import ValidationActions


def test_validate_resource_conf(resource_conf, si, logger):
    actions = ValidationActions(si, resource_conf, logger)
    actions.validate_resource_conf()
