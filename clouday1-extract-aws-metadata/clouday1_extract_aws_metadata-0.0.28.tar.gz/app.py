from flask import Flask, request
from flask_cors import CORS
import os
from command.initialize import Initialize
from command.collect import Collect
from command.prepare import Prepare
from dotenv import load_dotenv, find_dotenv
app=Flask(__name__)
CORS(app)
load_dotenv(find_dotenv())

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
@app.route('/')
def root_route():
    return 'Hello World'

@app.route('/newPost', methods=['POST'])
def initialize():
    # clear all the data inside the VM
    os.system('./tools/shell/jobClearJSON.sh')
    # get the input
    input=request.json
    print(AWS_ACCESS_KEY_ID)
    print(AWS_SECRET_ACCESS_KEY)

    # make class instance
    initialize_command=Initialize(input['region'], input['user_id'],
    input['account_name'],input['aws_access_key_id'],input['aws_secret_access_key'],
    input['aws_session_token'])
    # execute class function
    initialize_command.validate_input()
    initialize_command.check_identity()
    initialize_command.send_request_to_s3(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
    requestID=initialize_command.make_request(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
    print('The requestID is:', requestID)
    # print parameter inside class
    initialize_command.print_class_parameter()
    # get account id to initialize collect class
    account_id=initialize_command.get_account_id()

    # get the region
    regions=initialize_command.get_region()
    for region in regions:
        # initialize class
        collect_command = Collect(region,account_id)

        # call command functions
        collect_command.get_lambda_list()
        collect_command.get_lambda_policy()
        collect_command.list_sqs_queue()
        collect_command.get_sqs_queue()
        collect_command.list_sns_topic()
        collect_command.get_sns_topic_attribute()
        collect_command.list_dynamodb_table()
        collect_command.scan_dynamodb_table()
        collect_command.describe_dynamodb_table()
        collect_command.get_cloudtrail_start_sfn()
        collect_command.get_cloudtrail_translate_text()
        collect_command.get_cloudtrail_start_transcription_job()
        collect_command.get_apigw_rest_apis()
        collect_command.get_apigw_resources()
        collect_command.get_cloudtrail_waf_createWebACL()
        collect_command.get_cloudwatch_describe_log_groups()
        collect_command.get_cloudwatch_describe_log_stream()
        collect_command.get_cloudwatch_describe_log_event()
        collect_command.list_s3_bucket()
        collect_command.get_s3_bucket_policy()
        collect_command.describe_rds_instance()
        collect_command.describe_elbv2_load_balancer()
        collect_command.describe_elbv2_target_group()
        collect_command.describe_elbv2_target_health()
        collect_command.describe_ec2_instances()
        collect_command.describe_ec2_vpc_endpoint()
        collect_command.describe_ec2_subnets()
        collect_command.describe_ec2_security_groups()
        collect_command.describe_ec2_route_tables()
        collect_command.describe_ec2_network_interfaces()
        collect_command.describe_ec2_network_acls()
        collect_command.describe_ec2_describe_availability_zones()
        collect_command.describe_ec2_internet_gateway()
        collect_command.list_sfn()
        collect_command.describe_sfn()
        collect_command.list_waf_web_acl()
        collect_command.get_apigw_integration()
        collect_command.get_cloudwatch_cognito_event()
        collect_command.list_cognito_identity_pool()
        collect_command.get_s3_bucket_policy_status()
        collect_command.describe_cognito_identity_pools()
        collect_command.list_sns_tag()
        collect_command.list_sfn_tag()
        collect_command.list_ddb_tag()
        collect_command.list_s3_tag()
        collect_command.list_lambda_tag()

    # initialize a class
    for i in range(len(regions)):
        prepare_command = Prepare(regions[i], account_id)

        # prepare node logic
        prepare_command.prepare_lambda_node()
        prepare_command.prepare_s3_node()
        prepare_command.prepare_dynamodb_node()
        prepare_command.prepare_transcribe_node()
        prepare_command.prepare_translate_node()
        prepare_command.prepare_sns_node()
        prepare_command.prepare_sfn_node()
        prepare_command.prepare_apigw_node()
        prepare_command.prepare_cognito_node()
        # prepare edge logic
        prepare_command.find_sfn_connection()
        prepare_command.find_edge_lambda_to_sns()
        prepare_command.find_edge_lambda_to_ddb()
        prepare_command.find_edge_lambda_to_transcribe()
        prepare_command.find_edge_lambda_to_translate()
        prepare_command.find_edge_transcribe_to_s3()
        prepare_command.find_edge_s3_to_cognito()
        prepare_command.find_edge_lambda_to_sfn()
        prepare_command.find_edge_apigw_to_lambda()
        prepare_command.find_edge_sns_to_lambda()
        # EXPORT INTO JSON FILE
        if(i==len(regions)-1):
            prepare_command.exportToJSON()
            prepare_command.export_JSON_to_S3(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
            prepare_command.write_to_dynamoDB(str(requestID),AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
    return {  
        'status': 'Success',
        'code': 200,
        'message': 'Succeed creating and processing request'
    }

@app.route('/update',methods=['POST'])
def update():
    # clear all data inside VM
    os.system('./tools/shell/jobClearJSON.sh')
    # get the input from http
    input=request.json
    print(input)
    # initialize the Initialize Class
    initialize_command=Initialize('','','','','','')
    # execute the sequence for update
    initialize_command.process_requestID(input['requestID'],AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
    initialize_command.update_ddb_status(input['requestID'],AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
    initialize_command.get_credentials(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
    initialize_command.check_identity()
    # print the parameter inside Initialize Class
    initialize_command.print_class_parameter()
    # get account_id 
    account_id=initialize_command.get_account_id()
    # get the region
    regions=initialize_command.get_region()
    for region in regions:
        # initialize class
        collect_command = Collect(region,account_id)

        # call command functions
        collect_command.get_lambda_list()
        collect_command.get_lambda_policy()
        collect_command.list_sqs_queue()
        collect_command.get_sqs_queue()
        collect_command.list_sns_topic()
        collect_command.get_sns_topic_attribute()
        collect_command.list_dynamodb_table()
        collect_command.scan_dynamodb_table()
        collect_command.describe_dynamodb_table()
        collect_command.get_cloudtrail_start_sfn()
        collect_command.get_cloudtrail_translate_text()
        collect_command.get_cloudtrail_start_transcription_job()
        collect_command.get_apigw_rest_apis()
        collect_command.get_apigw_resources()
        collect_command.get_cloudtrail_waf_createWebACL()
        collect_command.get_cloudwatch_describe_log_groups()
        collect_command.get_cloudwatch_describe_log_stream()
        collect_command.get_cloudwatch_describe_log_event()
        collect_command.list_s3_bucket()
        collect_command.get_s3_bucket_policy()
        collect_command.describe_rds_instance()
        collect_command.describe_elbv2_load_balancer()
        collect_command.describe_elbv2_target_group()
        collect_command.describe_elbv2_target_health()
        collect_command.describe_ec2_instances()
        collect_command.describe_ec2_vpc_endpoint()
        collect_command.describe_ec2_subnets()
        collect_command.describe_ec2_security_groups()
        collect_command.describe_ec2_route_tables()
        collect_command.describe_ec2_network_interfaces()
        collect_command.describe_ec2_network_acls()
        collect_command.describe_ec2_describe_availability_zones()
        collect_command.describe_ec2_internet_gateway()
        collect_command.list_sfn()
        collect_command.describe_sfn()
        collect_command.list_waf_web_acl()
        collect_command.get_apigw_integration()
        collect_command.get_cloudwatch_cognito_event()
        collect_command.list_cognito_identity_pool()
        collect_command.get_s3_bucket_policy_status()
        collect_command.describe_cognito_identity_pools()
        collect_command.list_sns_tag()
        collect_command.list_sfn_tag()
        collect_command.list_ddb_tag()
        collect_command.list_s3_tag()
        collect_command.list_lambda_tag()

    # initialize a class
    for i in range(len(regions)):
        prepare_command = Prepare(regions[i], account_id)

        # prepare node logic
        prepare_command.prepare_lambda_node()
        prepare_command.prepare_s3_node()
        prepare_command.prepare_dynamodb_node()
        prepare_command.prepare_transcribe_node()
        prepare_command.prepare_translate_node()
        prepare_command.prepare_sns_node()
        prepare_command.prepare_sfn_node()
        prepare_command.prepare_apigw_node()
        prepare_command.prepare_cognito_node()
        # prepare edge logic
        prepare_command.find_sfn_connection()
        prepare_command.find_edge_lambda_to_sns()
        prepare_command.find_edge_lambda_to_ddb()
        prepare_command.find_edge_lambda_to_transcribe()
        prepare_command.find_edge_lambda_to_translate()
        prepare_command.find_edge_transcribe_to_s3()
        prepare_command.find_edge_s3_to_cognito()
        prepare_command.find_edge_lambda_to_sfn()
        prepare_command.find_edge_apigw_to_lambda()
        prepare_command.find_edge_sns_to_lambda()
        # EXPORT INTO JSON FILE
        if(i==len(regions)-1):
            prepare_command.exportToJSON()
            prepare_command.export_JSON_to_S3(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
            prepare_command.write_to_dynamoDB(str(input['requestID']),AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
    return {  
        'status': 'Success',
        'code': 200,
        'message': 'Succeed updating metadata file'
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)