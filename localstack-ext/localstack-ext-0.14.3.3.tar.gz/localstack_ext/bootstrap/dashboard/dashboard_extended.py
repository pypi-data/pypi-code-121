_A='rds'
import os
from localstack import config
from localstack.dashboard import infra as dashboard_infra
from localstack.utils.aws import aws_stack
from localstack.utils.aws.request_context import MARKER_APIGW_REQUEST_REGION,THREAD_LOCAL
from localstack.utils.bootstrap import is_api_enabled
from localstack.utils.common import run_safe,short_uid
from localstack_ext.bootstrap.aws_models import AmplifyApp,AppSyncAPI,CloudFrontDistribution,CodeCommitRepository,ElastiCacheCluster,RDSCluster,RDSDatabase,TransferServer
get_graph_orig=dashboard_infra.get_graph
def get_resources(fetch_func):
	try:A=[];fetch_func(A);return A
	except Exception:pass
	return[]
def get_rds_databases(name_filter,pool,env):
	if not is_api_enabled(_A):return[]
	def A(result):
		A=aws_stack.connect_to_service(_A);B=A.describe_db_instances()
		for C in B['DBInstances']:D=RDSDatabase(id=C['DBInstanceArn']);result.append(D)
	return get_resources(A)
def get_rds_clusters(name_filter,pool,env):
	if not is_api_enabled(_A):return[]
	def A(result):
		A=aws_stack.connect_to_service(_A);B=A.describe_db_clusters()
		for C in B['DBClusters']:D=RDSCluster(id=C['DBClusterArn']);result.append(D)
	return get_resources(A)
def get_appsync_apis(name_filter,pool,env):
	A='appsync'
	if not is_api_enabled(A):return[]
	def B(result):
		B=aws_stack.connect_to_service(A);C=B.list_graphql_apis()
		for D in C['graphqlApis']:E=AppSyncAPI(id=D['apiId']);result.append(E)
	return get_resources(B)
def get_amplify_apps(name_filter,pool,env):
	A='amplify'
	if not is_api_enabled(A):return[]
	def B(result):
		B=aws_stack.connect_to_service(A);C=B.list_apps()
		for D in C['apps']:E=AmplifyApp(id=D['appId']);result.append(E)
	return get_resources(B)
def get_elasticache_clusters(name_filter,pool,env):
	A='elasticache'
	if not is_api_enabled(A):return[]
	def B(result):
		B=aws_stack.connect_to_service(A);C=B.describe_cache_clusters()
		for D in C['CacheClusters']:E=ElastiCacheCluster(id=D['CacheClusterId']);result.append(E)
	return get_resources(B)
def get_transfer_servers(name_filter,pool,env):
	A='transfer'
	if not is_api_enabled(A):return[]
	def B(result):
		B=aws_stack.connect_to_service(A);C=B.list_servers()
		for D in C['Servers']:E=TransferServer(id=D['ServerId']);result.append(E)
	return get_resources(B)
def get_cloudfront_distributions(name_filter,pool,env):
	A='cloudfront'
	if not is_api_enabled(A):return[]
	def B(result):
		B=aws_stack.connect_to_service(A);C=B.list_distributions()
		for D in C['DistributionList']['Items']:E=CloudFrontDistribution(id=D['ARN']);result.append(E)
	return get_resources(B)
def get_codecommit_repos(name_filter,pool,env):
	A='codecommit'
	if not is_api_enabled(A):return[]
	def B(result):
		B=aws_stack.connect_to_service(A);C=B.list_repositories()
		for D in C['repositories']:E=CodeCommitRepository(id=D['repositoryId']);result.append(E)
	return get_resources(B)
def get_graph(*L,**D):
	K='nodes';J='AWS_SECRET_ACCESS_KEY';I='foobar';H='AWS_ACCESS_KEY_ID';os.environ[H]=os.environ.get(H)or I;os.environ[J]=os.environ.get(J)or I
	if hasattr(THREAD_LOCAL,'request_context'):M=D.get('region')or config.DEFAULT_REGION;THREAD_LOCAL.request_context.headers[MARKER_APIGW_REQUEST_REGION]=M
	F=run_safe(get_graph_orig,*(L),**D)or{K:[],'edges':[]};A=D.get('env');B=D.get('name_filter');C={};N={};O=get_rds_databases(B,pool=C,env=A);P=get_rds_clusters(B,pool=C,env=A);Q=get_appsync_apis(B,pool=C,env=A);R=get_amplify_apps(B,pool=C,env=A);S=get_elasticache_clusters(B,pool=C,env=A);T=get_transfer_servers(B,pool=C,env=A);U=get_cloudfront_distributions(B,pool=C,env=A);V=get_codecommit_repos(B,pool=C,env=A);W={'rds_db':O,'rds_cluster':P,'appsync_api':Q,'amplify_app':R,'elasticache_cluster':S,'transfer_server':T,'cloudfront_distr':U,'codecommit_repo':V}
	for (X,Y) in W.items():
		for E in Y:G=short_uid();N[E.id]=G;F[K].append({'id':G,'arn':E.id,'name':E.name(),'type':X})
	return F
def patch_dashboard():dashboard_infra.get_graph=get_graph