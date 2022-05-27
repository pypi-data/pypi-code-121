from awacs.aws import Allow, Action, Principal, Statement, Condition, MultiFactorAuthPresent, PolicyDocument, StringEquals
from paco.cftemplates.cftemplates import StackTemplate
from paco.utils import prefixed_name
from paco.models.references import get_model_obj_from_ref
import troposphere
import troposphere.ecr


class ECRRepository(StackTemplate):
    def __init__(self, stack, paco_ctx):
        ecr_repository = stack.resource
        super().__init__(stack, paco_ctx)
        self.set_aws_name('ECRRepository', self.resource_group_name, self.resource.name)

        self.init_template('Elastic Container Registry (ECR) Repository')
        if not ecr_repository.is_enabled(): return

        # Repository
        repo_dict = {
            'RepositoryName': ecr_repository.repository_name,
        }

        if ecr_repository.lifecycle_policy_text != None and ecr_repository.lifecycle_policy_text != "":
            repo_dict['LifecyclePolicy'] = troposphere.ecr.LifecyclePolicy(
                LifecyclePolicyText = ecr_repository.lifecycle_policy_text
            )
        if ecr_repository.lifecycle_policies != None and len(ecr_repository.lifecycle_policies.keys()) > 0:
            policy_rule_json_text = ""
            comma = ""
            for policy_id in ecr_repository.lifecycle_policies.keys():
                policy_config = ecr_repository.lifecycle_policies[policy_id]
                tag_prefix_list = ""
                count_unit = ""
                if len(policy_config.tag_prefix_list) > 0:
                    tag_prefix_list = '"tagPrefixList": ['
                    for tag_prefix in policy_config.tag_prefix_list:
                        tag_prefix_list += f'"{tag_prefix}"'
                    tag_prefix_list = '],'
                if policy_config.count_type == "sinceImagePushed":
                    count_unit = '"countUnit": "days",'

                policy_selection_json_text = f"""
            "selection": {{
                {count_unit}
                {tag_prefix_list}
                "tagStatus": "{policy_config.tag_status}",
                "countType": "{policy_config.count_type}",
                "countNumber": {policy_config.count_number}
            }},
"""
                policy_rule_json_text += f"""
        {{
            "rulePriority": {policy_config.rule_priority},
            "description": "{policy_config.description}",
            {policy_selection_json_text}
            "action": {{
                "type": "expire"
            }}
        }}{comma}
"""
                comma=","
            policy_json_text = f"""
{{
    "rules": [
        {policy_rule_json_text}
    ]
}}
"""
            repo_dict['LifecyclePolicy'] = {
                "LifecyclePolicyText": policy_json_text,
            }
        if ecr_repository.repository_policy != None or ecr_repository.cross_account_access != []:
            policy_statements = []
            if ecr_repository.repository_policy != None:
                index = 0
                for policy_statement in ecr_repository.repository_policy.statement:
                    statement_dict = {
                        'Sid': f'Policy{index}',
                        'Effect': policy_statement.effect,
                        'Action': [
                            Action(*action.split(':')) for action in policy_statement.action
                        ]
                    }
                    if policy_statement.principal != None:
                        if len(policy_statement.principal.aws) > 0:
                            statement_dict['Principal'] = Principal("AWS", policy_statement.principal.aws)
                        elif len(policy_statement.principal.service) > 0:
                            statement_dict['Principal'] = Principal("Service", policy_statement.principal.service)
                    policy_statements.append(
                        Statement(**statement_dict)
                    )
                    index += 1
            if ecr_repository.cross_account_access != []:
                account_ids = []
                for account_ref in ecr_repository.cross_account_access:
                    account = get_model_obj_from_ref(account_ref, self.paco_ctx.project)
                    account_ids.append(account.account_id)
                statement_dict = {
                    'Sid': 'AllowCrossAccountAccess',
                    'Effect': 'Allow',
                    'Action': [
                        Action('ecr', 'BatchCheckLayerAvailability'),
                        Action('ecr', 'BatchGetImage'),
                        Action('ecr', 'CompleteLayerUpload'),
                        Action('ecr', 'DescribeImageScanFindings'),
                        Action('ecr', 'DescribeImages'),
                        Action('ecr', 'DescribeRepositories'),
                        Action('ecr', 'GetAuthorizationToken'),
                        Action('ecr', 'GetDownloadUrlForLayer'),
                        Action('ecr', 'GetLifecyclePolicy'),
                        Action('ecr', 'GetLifecyclePolicyPreview'),
                        Action('ecr', 'GetRepositoryPolicy'),
                        Action('ecr', 'InitiateLayerUpload'),
                        Action('ecr', 'ListImages'),
                        Action('ecr', 'ListTagsForResource'),
                        Action('ecr', 'PutImage'),
                        Action('ecr', 'UploadLayerPart'),
                    ],
                    'Principal': Principal("AWS", account_ids),
                }
                policy_statements.append(Statement(**statement_dict))
            repo_dict['RepositoryPolicyText'] = PolicyDocument(
                Version="2012-10-17",
                Statement=policy_statements
            )
        repository_res = troposphere.ecr.Repository.from_dict(
            'Repository', repo_dict
        )

        # Outputs
        self.create_output(
            title=repository_res.title + 'Arn',
            description="ECR Repository Arn",
            value=troposphere.GetAtt(repository_res, 'Arn'),
            ref=ecr_repository.paco_ref_parts + ".arn")

        self.template.add_resource(repository_res)