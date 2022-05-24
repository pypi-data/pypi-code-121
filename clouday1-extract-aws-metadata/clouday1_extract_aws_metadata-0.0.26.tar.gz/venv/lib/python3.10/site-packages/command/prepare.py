from clouday1_extract_aws_metadata import export_to_JSON
from clouday1_extract_aws_metadata import lambda_node_prepare
from clouday1_extract_aws_metadata import s3_prepare_node
from clouday1_extract_aws_metadata import dynamodb_prepare_node
from clouday1_extract_aws_metadata import transcribe_prepare_node
from clouday1_extract_aws_metadata import translate_prepare_node
from clouday1_extract_aws_metadata import sns_prepare_node
from clouday1_extract_aws_metadata import sfn_prepare_node
from clouday1_extract_aws_metadata import apigw_prepare_node
from clouday1_extract_aws_metadata import cognito_prepare_node
from clouday1_extract_aws_metadata import sfn_find_connection
from clouday1_extract_aws_metadata import edge_apigw_to_lambda_find
from clouday1_extract_aws_metadata import edge_sns_to_lambda_find
from clouday1_extract_aws_metadata import edge_lambda_ddb_find
from clouday1_extract_aws_metadata import edge_lambda_to_transcribe
from clouday1_extract_aws_metadata import edge_lambda_to_translate
from clouday1_extract_aws_metadata import edge_s3_to_cognito_find
from clouday1_extract_aws_metadata import edge_lambda_sns_find
from clouday1_extract_aws_metadata import edge_transcribe_to_s3_find
from clouday1_extract_aws_metadata import edge_lambda_to_sfn_find
from clouday1_extract_aws_metadata import export_to_s3
class Prepare:
    def __init__(self, region_name, account_id):
        self.region_name = region_name
        self.account_id = account_id
        self.cytoscape_node_data = []
        self.cytoscape_edge_data = []

    def exportToJSON(self):
        export_to_JSON.export_to_JSON(self.cytoscape_node_data, self.cytoscape_edge_data)

    def prepare_lambda_node(self):
        lambda_node_prepare.lambda_prepare_node(self.region_name, self.account_id,
                            self.cytoscape_node_data)

    def prepare_s3_node(self):
        s3_prepare_node.s3_prepare_node(self.region_name, self.account_id,
                        self.cytoscape_node_data)

    def prepare_dynamodb_node(self):
        dynamodb_prepare_node.dynamodb_prepare_node(
            self.region_name, self.account_id, self.cytoscape_node_data)

    def prepare_transcribe_node(self):
        transcribe_prepare_node.transcribe_prepare_node(
            self.region_name, self.account_id, self.cytoscape_node_data)

    def prepare_translate_node(self):
        translate_prepare_node.translate_prepare_node(
            self.region_name, self.account_id, self.cytoscape_node_data)

    def prepare_sns_node(self):
        sns_prepare_node.sns_prepare_node(self.region_name, self.account_id,
                         self.cytoscape_node_data)

    def prepare_sfn_node(self):
        sfn_prepare_node.sfn_prepare_node(self.region_name, self.account_id,
                         self.cytoscape_node_data)

    def prepare_apigw_node(self):
        apigw_prepare_node.api_gw_prepare_node(self.region_name, self.account_id,
                            self.cytoscape_node_data)

    def prepare_cognito_node(self):
        cognito_prepare_node.cognito_prepare_node(
            self.region_name, self.account_id, self.cytoscape_node_data)

    def find_sfn_connection(self):
        sfn_find_connection.sfn_find_connection(self.cytoscape_node_data, self.cytoscape_edge_data)

    def find_edge_lambda_to_sns(self):
        edge_lambda_sns_find.edge_lambda_sns_find(self.cytoscape_edge_data, self.region_name)

    def find_edge_lambda_to_ddb(self):
        edge_lambda_ddb_find.edge_lambda_ddb_find(self.cytoscape_edge_data, self.region_name)

    def find_edge_lambda_to_transcribe(self):
        edge_lambda_to_transcribe.edge_lambda_to_transcribe(
            self.cytoscape_edge_data, self.region_name, self.account_id)

    def find_edge_lambda_to_translate(self):
        edge_lambda_to_translate.edge_lambda_to_translate_find(
            self.cytoscape_edge_data, self.region_name, self.account_id)

    def find_edge_transcribe_to_s3(self):
        edge_transcribe_to_s3_find.edge_transcribe_to_s3_find(
            self.cytoscape_edge_data, self.region_name, self.account_id)

    def find_edge_s3_to_cognito(self):
        edge_s3_to_cognito_find.edge_s3_to_cognito_find(
            self.cytoscape_edge_data)

    def find_edge_lambda_to_sfn(self):
        edge_lambda_to_sfn_find.edge_lambda_to_sfn_find(self.region_name,
                                self.cytoscape_edge_data)

    def find_edge_apigw_to_lambda(self):
        edge_apigw_to_lambda_find.edge_apigw_to_lambda_find(
            self.cytoscape_edge_data, self.cytoscape_node_data)

    def find_edge_sns_to_lambda(self):
        edge_sns_to_lambda_find.edge_sns_to_lambda_find(self.cytoscape_edge_data)
    
    def export_JSON_to_S3(self,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY):
        export_to_s3.upload_to_S3(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)

    def write_to_dynamoDB(self,requestID,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY):
        export_to_s3.write_to_dynamo_db(requestID,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
