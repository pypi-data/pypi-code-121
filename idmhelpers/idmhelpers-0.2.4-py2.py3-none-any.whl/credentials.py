# Module to help setting configuration to acccess Azure Storage
#

class Credentials:
    """
    Helper class for Databricks credentials


    setSparkConf
    setStorageCredentialsPassthrough
    setStorageCredentialsSPN
    setStorageCredentialsKey
    getHadoopConfig

    To use:

    from idmhelpers.credentials import Credentials
    credhelper=Credentials(spark,dbutils)
    credhelper.setStorageCredentials('myscope','az21p1se11')
    """

    dbutils = None
    spark = None

    def __init__(self, spark, dbutils):
        self.spark = spark
        self.dbutils = dbutils

    def setSparkConf(self, key, value):
        """
        Set Spark configuration and Hadoop configuration for the key value.
        """
        self.spark.conf.set(key, value)
        # Hadoop configuration is required when using the RDD APIs.
        hadoopConfig = self.spark._jsc.hadoopConfiguration()
        self.spark.conf.set("spark.hadoop."+key, value)
        hadoopConfig.set(key, value)

    def setStorageCredentialsPassthrough(self, account=None):
        """
        Databricks: Set configuration to use credential passthrough to access Azure Storage Accounts
        If account is missing or None - this is set at global level for all accounts.
        """
        if account != None:
            suffix = ".{account}.dfs.core.windows.net"
        else:
            suffix = ""
        self.setSparkConf(
            "fs.azure.account.auth.type{suffix}", "CustomAccessToken")
        self.setSparkConf("fs.azure.account.custom.token.provider.class", self.spark.conf.get(
            "spark.databricks.passthrough.adls.tokenProviderClassName"))

    def setStorageCredentialsSPN(self, scope, spn_name, account=None):
        """
        Databricks: Set configuration to use an SPN/OAuth to access Azure Storage Accounts
        If account is missing or None - this is set at global level for all accounts.
        Expects the secrets to be
            {spn_name}-spn-tenant
            {spn_name}-spn-id
            {spn_name}-spn-secret        
        """
        tenandId = self.dbutils.secrets.get(scope, f'{spn_name}-spn-tenant')
        applicationId = self.dbutils.secrets.get(scope, f'{spn_name}-spn-id')
        applicationSecret = self.dbutils.secrets.get(
            scope, f'{spn_name}-spn-secret')
        endpoint = "https://login.microsoftonline.com/" + tenandId + "/oauth2/token"
        if account != None:
            suffix = ".{account}.dfs.core.windows.net"
        else:
            suffix = ""
        self.setSparkConf(f"fs.azure.account.auth.type{suffix}", "OAuth")
        self.setSparkConf(f"fs.azure.account.oauth.provider.type{suffix}",
                          "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider")
        self.setSparkConf(
            f"fs.azure.account.oauth2.client.id{suffix}", applicationId)
        self.setSparkConf(
            f"fs.azure.account.oauth2.client.secret{suffix}", applicationSecret)
        self.setSparkConf(
            f"fs.azure.account.oauth2.client.endpoint{suffix}", endpoint)

    def setStorageCredentialsKey(self, scope, account):
        """
        Databricks: Set configuration to use Storage Key to access Azure Storage Accounts
        Expects the storage key to be stored as {account}-storage-access-key
        """
        secret = self.dbutils.secrets.get(
            scope, f'{account}-storage-access-key')
        self.setSparkConf(
            f"fs.azure.account.auth.type.{account}.dfs.core.windows.net", "SharedKey")
        self.setSparkConf(
            f"fs.azure.account.key.{account}.dfs.core.windows.net", secret)

    def getHadoopConfig(self):
        """
        Retrieve the entire hadoop configuration
        """
        hadoop_config = self.spark._jsc.hadoopConfiguration()
        hadoop_config_dict = {
            e.getKey(): e.getValue()
            for e in hadoop_config.iterator()
        }

        # Sort by key and print the result
        hadoop_config_dict = {
            k: hadoop_config_dict[k]
            for k in sorted(hadoop_config_dict)
        }
        return hadoop_config_dict
