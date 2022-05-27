AMAZON_CLOUDWATCH_FULL_ACCESS_POLICY_ARN = (
    "arn:aws:iam::aws:policy/CloudWatchFullAccess"
)
AMAZON_EC2_FULL_ACCESS_POLICY_ARN = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
AMAZON_IAM_FULL_ACCESS_POLICY_ARN = "arn:aws:iam::aws:policy/IAMFullAccess"
AMAZON_ROUTE53_FULL_ACCESS_POLICY_ARN = (
    "arn:aws:iam::aws:policy/AmazonRoute53FullAccess"
)
AMAZON_S3_FULL_ACCESS_POLICY_ARN = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
AMAZON_VPC_FULL_ACCESS_POLICY_ARN = "arn:aws:iam::aws:policy/AmazonVPCFullAccess"

EKS_FULL_ACCESS_POLICY_NAME = "EKSFullAccess"
EKS_FULL_ACCESS_POLICY_DOCUMENT = {
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Action": ["eks:*"], "Resource": "*"}],
}

AMAZON_ECR_READONLY_ACCESS_POLICY_ARN = (
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
)

ANYSCALE_IAM_ACCESS_POLICY_NAME = "AnyscaleIAMAccess"
ANYSCALE_IAM_ACCESS_POLICY_DOCUMENT = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "OrganizationalPolicies",
            "Action": [
                "organizations:DescribeAccount",
                "organizations:DescribeOrganization",
                "organizations:DescribeOrganizationalUnit",
                "organizations:DescribePolicy",
                "organizations:ListChildren",
                "organizations:ListParents",
                "organizations:ListPoliciesForTarget",
                "organizations:ListRoots",
                "organizations:ListPolicies",
                "organizations:ListTargetsForPolicy",
            ],
            "Effect": "Allow",
            "Resource": "*",
        },
        {
            "Sid": "IAMReadAll",
            "Action": ["iam:Get*", "iam:List*"],
            "Effect": "Allow",
            "Resource": "*",
        },
        {
            "Sid": "SpecificIAMWriteActions",
            "Action": [
                "iam:AddClientIDToOpenIDConnectProvider",
                "iam:AddRoleToInstanceProfile",
                "iam:AttachRolePolicy",
                "iam:CreateInstanceProfile",
                "iam:CreateOpenIDConnectProvider",
                "iam:CreatePolicy",
                "iam:CreatePolicyVersion",
                "iam:CreateRole",
                "iam:CreateServiceLinkedRole",
                "iam:DeleteInstanceProfile",
                "iam:DeleteOpenIDConnectProvider",
                "iam:DeletePolicy",
                "iam:DeletePolicyVersion",
                "iam:DeleteRole",
                "iam:DeleteRolePolicy",
                "iam:DeleteServiceLinkedRole",
                "iam:DetachRolePolicy",
                "iam:PassRole",
                "iam:PutRolePermissionsBoundary",
                "iam:PutRolePolicy",
                "iam:RemoveClientIDFromOpenIDConnectProvider",
                "iam:RemoveRoleFromInstanceProfile",
                "iam:SetDefaultPolicyVersion",
                "iam:TagInstanceProfile",
                "iam:TagOpenIDConnectProvider",
                "iam:TagPolicy",
                "iam:TagRole",
                "iam:UntagInstanceProfile",
                "iam:UntagOpenIDConnectProvider",
                "iam:UntagPolicy",
                "iam:UntagRole",
                "iam:UpdateAssumeRolePolicy",
                "iam:UpdateOpenIDConnectProviderThumbprint",
                "iam:UpdateRole",
                "iam:UpdateRoleDescription",
            ],
            "Effect": "Allow",
            "Resource": "*",
        },
    ],
}
