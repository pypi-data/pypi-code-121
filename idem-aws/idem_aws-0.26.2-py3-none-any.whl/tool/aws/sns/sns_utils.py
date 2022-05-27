import json


def get_default_topic_policy(hub, topic_arn: str) -> str:
    default_policy = {
        "Version": "2008-10-17",
        "Id": "__default_policy_ID",
        "Statement": [
            {
                "Sid": "__default_statement_ID",
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": [
                    "SNS:GetTopicAttributes",
                    "SNS:SetTopicAttributes",
                    "SNS:AddPermission",
                    "SNS:RemovePermission",
                    "SNS:DeleteTopic",
                    "SNS:Subscribe",
                    "SNS:ListSubscriptionsByTopic",
                    "SNS:Publish",
                ],
                "Resource": "topic_arn",
                "Condition": {"StringEquals": {"AWS:SourceOwner": "acct_id"}},
            }
        ],
    }
    default_policy["Statement"][0]["Resource"] = topic_arn
    acct_id = topic_arn.split(":")[4]
    default_policy["Statement"][0]["Condition"]["StringEquals"][
        "AWS:SourceOwner"
    ] = acct_id
    policy = json.dumps(default_policy, separators=(", ", ": "))
    return policy
