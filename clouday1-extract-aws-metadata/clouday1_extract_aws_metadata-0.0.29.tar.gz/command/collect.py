from clouday1_extract_aws_metadata import lambda_list_function
from clouday1_extract_aws_metadata import lambda_get_policy
from clouday1_extract_aws_metadata import sqs_list_queue
from clouday1_extract_aws_metadata import sqs_get_queue
from clouday1_extract_aws_metadata import sns_list_topic
from clouday1_extract_aws_metadata import sns_get_topic_attribute
from clouday1_extract_aws_metadata import dynamodb_list_table
from clouday1_extract_aws_metadata import dynamodb_scan
from clouday1_extract_aws_metadata import cloudtrail_sfn_start_execution
from clouday1_extract_aws_metadata import cloudtrail_translate_text
from clouday1_extract_aws_metadata import cloudtrail_start_transcription_job
from clouday1_extract_aws_metadata import apigw_get_rest_apis
from clouday1_extract_aws_metadata import apigw_get_resources
from clouday1_extract_aws_metadata import cloudtrail_waf_createWebACL
from clouday1_extract_aws_metadata import cloudwatch_describe_log_groups
from clouday1_extract_aws_metadata import cloudwatch_describe_log_stream
from clouday1_extract_aws_metadata import cloudwatch_get_log_event
from clouday1_extract_aws_metadata import s3_list_bucket
from clouday1_extract_aws_metadata import s3_get_bucket_policy
from clouday1_extract_aws_metadata import s3_get_bucket_policy_status
from clouday1_extract_aws_metadata import rds_describe_instance
from clouday1_extract_aws_metadata import elbv2_describe_load_balancer
from clouday1_extract_aws_metadata import elbv2_describe_target_group
from clouday1_extract_aws_metadata import elbv2_describe_target_health
from clouday1_extract_aws_metadata import ec2_describe_instances
from clouday1_extract_aws_metadata import ec2_describe_vpc_endpoint
from clouday1_extract_aws_metadata import ec2_describe_subnet
from clouday1_extract_aws_metadata import ec2_describe_security_group
from clouday1_extract_aws_metadata import ec2_describe_route_tables
from clouday1_extract_aws_metadata import ec2_describe_network_interfaces
from clouday1_extract_aws_metadata import ec2_describe_network_acls
from clouday1_extract_aws_metadata import ec2_describe_availability_zones
from clouday1_extract_aws_metadata import ec2_describe_internet_gateway
from clouday1_extract_aws_metadata import sfn_list
from clouday1_extract_aws_metadata import sfn_describe
from clouday1_extract_aws_metadata import waf_list_resource_web_acls
from clouday1_extract_aws_metadata import apigw_get_integration
from clouday1_extract_aws_metadata import cloudwatch_get_cognito_log_event
from clouday1_extract_aws_metadata import dynamodb_describe_table
from clouday1_extract_aws_metadata import cognito_list_identity_pool
from clouday1_extract_aws_metadata import cognito_describe_identity_pools
from clouday1_extract_aws_metadata import sns_list_tags
from clouday1_extract_aws_metadata import sfn_list_tags
from clouday1_extract_aws_metadata import dynamodb_list_tags_of_resource
from clouday1_extract_aws_metadata import s3_get_bucket_tagging
from clouday1_extract_aws_metadata import lambda_list_tags

'''Collect class for collecting data from AWS Services'''
class Collect:
    '''Collect class for collecting data from AWS Lambda'''

    def __init__(self, region_name,account_id):
        self.region_name = region_name
        self.account_id=account_id

    def get_lambda_list(self):
        lambda_list_function.lambda_list_function(self.region_name)

    def get_lambda_policy(self):
        lambda_get_policy.lambda_get_policy(self.region_name)

    def list_sqs_queue(self):
        sqs_list_queue.sqs_list_queue(self.region_name)

    def get_sqs_queue(self):
        sqs_get_queue.sqs_get_queue(self.region_name)

    def list_sns_topic(self):
        sns_list_topic.sns_list_topic(self.region_name)

    def get_sns_topic_attribute(self):
        sns_get_topic_attribute.sns_get_topic_attribute(self.region_name)

    def list_dynamodb_table(self):
        dynamodb_list_table.dynamodb_list_table(self.region_name)

    def scan_dynamodb_table(self):
        dynamodb_scan.dynamodb_scan(self.region_name)

    def get_cloudtrail_start_sfn(self):
        cloudtrail_sfn_start_execution.cloudtrail_start_sfn(self.region_name)

    def get_cloudtrail_translate_text(self):
        cloudtrail_translate_text.cloudtrail_translate_text(self.region_name)

    def get_cloudtrail_start_transcription_job(self):
        cloudtrail_start_transcription_job.cloudtrail_start_transcription_job(self.region_name)

    def get_apigw_rest_apis(self):
        apigw_get_rest_apis.apigw_get_rest_apis(self.region_name)

    def get_apigw_resources(self):
        apigw_get_resources.apigw_get_resource(self.region_name)

    def get_cloudtrail_waf_createWebACL(self):
        cloudtrail_waf_createWebACL.cloudtrail_waf_createWebACL(self.region_name)

    def get_cloudwatch_describe_log_groups(self):
        cloudwatch_describe_log_groups.cloudwatch_describe_log_groups(self.region_name)

    def get_cloudwatch_describe_log_stream(self):
        cloudwatch_describe_log_stream.cloudwatch_describe_log_stream(self.region_name)

    def get_cloudwatch_describe_log_event(self):
        cloudwatch_get_log_event.cloudwatch_describe_log_event(self.region_name)

    def list_s3_bucket(self):
        s3_list_bucket.s3_list_bucket(self.region_name)

    def get_s3_bucket_policy(self):
        s3_get_bucket_policy.s3_get_bucket_policy(self.region_name)

    def get_s3_bucket_policy_status(self):
        s3_get_bucket_policy_status.s3_get_bucket_policy_status(self.region_name)

    def describe_rds_instance(self):
        rds_describe_instance.rds_describe_instance(self.region_name)

    def describe_elbv2_load_balancer(self):
        elbv2_describe_load_balancer.elbv2_describe_load_balancer(self.region_name)

    def describe_elbv2_target_group(self):
        elbv2_describe_target_group.elbv2_describe_target_group(self.region_name)

    def describe_elbv2_target_health(self):
        elbv2_describe_target_health.elbv2_describe_target_health(self.region_name)

    def describe_ec2_instances(self):
        ec2_describe_instances.ec2_describe_instances(self.region_name)

    def describe_ec2_vpc_endpoint(self):
        ec2_describe_vpc_endpoint.ec2_describe_vpc_endpoint(self.region_name)

    def describe_ec2_subnets(self):
        ec2_describe_subnet.ec2_describe_subnets(self.region_name)

    def describe_ec2_security_groups(self):
        ec2_describe_security_group.ec2_describe_security_group(self.region_name)

    def describe_ec2_route_tables(self):
        ec2_describe_route_tables.ec2_describe_route_tables(self.region_name)

    def describe_ec2_network_interfaces(self):
        ec2_describe_network_interfaces.ec2_describe_network_interfaces(self.region_name)

    def describe_ec2_network_acls(self):
        ec2_describe_network_acls.ec2_describe_network_acls(self.region_name)

    def describe_ec2_describe_availability_zones(self):
        ec2_describe_availability_zones.ec2_describe_availability_zone(self.region_name)

    def describe_ec2_internet_gateway(self):
        ec2_describe_internet_gateway.ec2_describe_internet_gateway(self.region_name)

    def list_sfn(self):
        sfn_list.sfn_list(self.region_name)

    def describe_sfn(self):
        sfn_describe.sfn_describe(self.region_name)

    def list_waf_web_acl(self):
        waf_list_resource_web_acls.waf_list_resource_web_acl(self.region_name)

    def get_apigw_integration(self):
        apigw_get_integration.apigw_get_integration(self.region_name)

    def get_cloudwatch_cognito_event(self):
        cloudwatch_get_cognito_log_event.cloudwatch_get_cognito_log_event(self.region_name)

    def list_cognito_identity_pool(self):
        cognito_list_identity_pool.cognito_list_identity_pool(self.region_name)

    def describe_dynamodb_table(self):
        dynamodb_describe_table.dynamodb_describe_table(self.region_name)

    def describe_cognito_identity_pools(self):
        cognito_describe_identity_pools.cognito_describe_identity_pools(self.region_name)

    def list_sns_tag(self):
        sns_list_tags.sns_list_tags(self.region_name)
    
    def list_sfn_tag(self):
        sfn_list_tags.sfn_list_tags(self.region_name)

    def list_ddb_tag(self):
        dynamodb_list_tags_of_resource.ddb_list_tags_of_resource(self.region_name,
        self.account_id)
    
    def list_s3_tag(self):
        s3_get_bucket_tagging.s3_get_bucket_tagging(self.region_name)
    
    def list_lambda_tag(self):
        lambda_list_tags.lambda_list_tags(self.region_name)