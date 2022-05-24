#!/usr/bin/env/python
# from optparse import OptionError
from requests.structures import CaseInsensitiveDict
import requests
import os
from minio import Minio
menu_options = {
    1: 'Install MySQL-Operator',
    2: 'Create MySQL-Cluster',
    3: 'Create Cluster from existing backup',
    4: 'List Your Clusters',
    5: 'Edit Cluster',  # change backup , change replica
    6: 'Remove Cluster',
    7: 'List Backups',
    8: 'Exit',
}

# Menu for edit cluster options
menu_edit_cluster = {
    1: 'Change number of replica',
    2: 'Change backup schedule',
}
helm_chart_path = os.path.join(os.path.dirname(__file__), "mysql-cluster")


def print_menu():
    for key in menu_options.keys():
        print(key, '--', menu_options[key])


def print_edit_cluster_menu():
    for key in menu_edit_cluster.keys():
        print(key, '--', menu_edit_cluster[key])


def create_server_pool_lb(api_url, customer_id, cloudspace_id,
                          cluster_name, node_port, jwt):
    # Create server pool and Loadbalancer using API
    # make session
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer {}".format(jwt)

    ##################################################
    print("Creating serverpool...")
    # Create ServerPool
    serverpool_api = f"https://{api_url}/alpha/customers/{customer_id}/cloudspaces/{cloudspace_id}\
/ingress/server-pools?name={cluster_name}"

    # Make API request to create Serverpool
    create_serverpool = requests.post(serverpool_api, headers=headers)
    serverpool = create_serverpool.json()

    # save serverpool id to var "serverpool_id"
    serverpool_id = serverpool['id']
    print(f"ServerPool Status {create_serverpool.status_code}")

    print("Add kubernetes hosts to serverpool...")
    # Get k8s ips
    k8s_node_ip = "kubectl get node -o wide"
    output = os.popen(k8s_node_ip).read()
    mylist = []
    for line in output.splitlines():
        fields = line.split()
        # Save output to list
        mylist.append(fields)
    # Remove first row
    mylist.remove(mylist[0])
    # print list line by line with grep IPs
    for line in mylist:
        ip = line[5]
        # API URL for post request to add host to server pool
        add_host_to_serverpool_api = f"https://{api_url}/alpha/customers/\
{customer_id}/cloudspaces/{cloudspace_id}/\
ingress/server-pools/{serverpool_id}/\
hosts?address={ip}"
        # Create API request to add host to server pool
        add_host = requests.post(add_host_to_serverpool_api, headers=headers)

        print(add_host.json())

    print(f"Add hosts to ServerPool Status {add_host.status_code}")
    ##################################################

    # Create LB
    print("Creating LoadBalancer...")
    lb_api = f"https://{api_url}/alpha/customers/{customer_id}/cloudspaces/\
{cloudspace_id}/ingress/load-balancers"
    # Create MySQL LB
    create_mysql_lb = requests.post(lb_api, headers=headers, json={
        "name": f"{cluster_name}",
        "description": "string",
        "type": "TCP",
        "front_end": {
            "port": node_port,
            "tls": {
                "is_enabled": False,
                "domain": "string",
                "tls_termination": False
                }
            },
        "back_end": {
            "serverpool_id": f"{serverpool_id}",
            "target_port": node_port
        }
        })
    print(create_mysql_lb.json())


def create_bucket(s3_url, s3_port, s3_access_key, s3_secret_key, mybucket):
    endpoint_url = f"{s3_url}:{s3_port}"
    s3_access = f"{s3_access_key}"
    s3_secret = f"{s3_secret_key}"
    client = Minio(
        endpoint=endpoint_url,
        secure=True,
        access_key=s3_access,
        secret_key=s3_secret
    )
    found = client.bucket_exists(mybucket)
    if not found:
        client.make_bucket(mybucket)
        print(f"Bucket {mybucket} has been created")
    else:
        print(f"Bucket {mybucket} already exists")


def test_s3_connection(s3_url, s3_port, s3_access_key, s3_secret_key):
    endpoint_url = f"{s3_url}:{s3_port}"
    s3_access = f"{s3_access_key}"
    s3_secret = f"{s3_secret_key}"
    client = Minio(
        endpoint=endpoint_url,
        secure=True,
        access_key=s3_access,
        secret_key=s3_secret
    )
    try:
        client.list_buckets()
        print("Object storage connected")

    except Exception:
        print("Object storage not reachable")
        exit(0)


def install_mysql_operator():
    print('Installing MySQL-Operator...')
    add_helm_repo = 'helm repo add bitpoke https://helm-charts.bitpoke.io'
    os.popen(add_helm_repo).read()
    update_helm_repo = 'helm repo update'
    os.popen(update_helm_repo).read()
    install_mysql_operator = "helm install mysql-operator \
bitpoke/mysql-operator"
    os.popen(install_mysql_operator).read()
    print("MySQL-Operator is installed")


def create_cluster():
    print('Create MySQL-Cluster')
    jwt = input("JWT: ")
    # ex: cloud.gig.tech/api/1
    api_url = input("API URL: ")
    customer_id = input("Customer ID: ")
    cloudspace_id = input("CloudSpace ID: ")
    cluster_name = input("Cluster Name: ")
    replica = input("Number of replicas: ")
    root_password = input("Root Password:  ")
    node_port = int(input("MySQL NodePort [30000-32767]: "))
    pvc_size = input("Cluster Size (Gi): ")
    answer = None
    while answer not in ("yes", "no", "y", "Y", "n", "N"):
        answer = input("Enable Auto backup ? [yes/no]: ")
        if answer == "yes" or answer == "y" or answer == "Y":
            backup_schedule = None
            while backup_schedule not in ("daily", "weekly", "monthly",
                                          "yearly", "d", "D", "w", "W", "m",
                                          "M", "y", "Y", "custom", "c", "C"):
                backup_schedule = input("Backup Schedule [daily/weekly/\
monthly/yearly/custom]: ")
                if backup_schedule == "daily" or backup_schedule == "d" or\
                   backup_schedule == "D":
                    my_backup_schedule = "0 0 0 * * *"
                    backup_history_limit = input("Number of backups limit: ")
                    s3_url = input("Object storage endpoint: ")
                    s3_port = input("Object storage port: ")
                    s3_access_key = input("Object storage access key: ")
                    s3_secret_key = input("Object storage secret key: ")
                    mybucket = input("Bucket Name: ")
                elif backup_schedule == "weekly" or backup_schedule == "w" or\
                        backup_schedule == "W":
                    my_backup_schedule = "0 0 0 * * 0"
                    backup_history_limit = input("Number of backups limit: ")
                    s3_url = input("Object storage endpoint: ")
                    s3_port = input("Object storage port: ")
                    s3_access_key = input("Object storage access key: ")
                    s3_secret_key = input("Object storage secret key: ")
                    mybucket = input("Bucket Name: ")
                elif backup_schedule == "monthly" or backup_schedule == "m" or\
                        backup_schedule == "M":
                    my_backup_schedule = "0 0 0 1 * *"
                    backup_history_limit = input("Number of backups limit: ")
                    s3_url = input("Object storage endpoint: ")
                    s3_port = input("Object storage port: ")
                    s3_access_key = input("Object storage access key: ")
                    s3_secret_key = input("Object storage secret key: ")
                    mybucket = input("Bucket Name: ")
                elif backup_schedule == "yearly" or backup_schedule == "y" or\
                        backup_schedule == "Y":
                    my_backup_schedule = "15 0 0 1 1 *"
                    backup_history_limit = input("Number of backups limit: ")
                    s3_url = input("Object storage endpoint: ")
                    s3_port = input("Object storage port: ")
                    s3_access_key = input("Object storage access key: ")
                    s3_secret_key = input("Object storage secret key: ")
                    mybucket = input("Bucket Name: ")
                elif backup_schedule == "custom" or backup_schedule == "c" or\
                        backup_schedule == "C":
                    my_backup_schedule = input("Custom backup cronjob: ")
                    backup_history_limit = input("Number of backups limit: ")
                    s3_url = input("Object storage endpoint: ")
                    s3_port = input("Object storage port: ")
                    s3_access_key = input("Object storage access key: ")
                    s3_secret_key = input("Object storage secret key: ")
                    mybucket = input("Bucket Name: ")
                else:
                    print("Error please enter correct value")
            # Test S3
            test_s3_connection(s3_url, s3_port, s3_access_key, s3_secret_key)
            create_bucket(s3_url, s3_port, s3_access_key,
                          s3_secret_key, mybucket)
            # DEF CREATE SERVER POOL & LB
            create_server_pool_lb(api_url, customer_id, cloudspace_id,
                                  cluster_name, node_port, jwt)
            # Deploy cluster with backup
            print("Deploying your cluster with auto backup...")
            # helm_chart_path
            command2 = f'helm install {cluster_name} {helm_chart_path} --set replicas={replica} \
--set rootPassword={root_password} \
--set mysqlnodeport={node_port} \
--set backupSchedule="{my_backup_schedule}" \
--set backupScheduleJobsHistoryLimit={backup_history_limit} \
--set backupRemoteDeletePolicy=delete \
--set backupURL="s3://{mybucket}/" \
--set backupCredentials.AWS_ACCESS_KEY_ID="{s3_access_key}" \
--set backupCredentials.AWS_SECRET_ACCESS_KEY="{s3_secret_key}" \
--set backupCredentials.S3_PROVIDER=Minio \
--set backupCredentials.S3_ENDPOINT=https://{s3_url} \
--set volumeSpec.persistentVolumeClaim.resources.requests.storage={pvc_size}Gi'
            output2 = os.popen(command2).read()
            print(output2)
            print("Please wait until the cluster becomes ready...")
            print(f"Access your cluster with port {node_port} \n")
        elif answer == "no" or answer == "n" or answer == "N":
            # Deploy cluster without backup
            # DEF CREATE SERVER POOL & LB
            create_server_pool_lb(api_url, customer_id, cloudspace_id,
                                  cluster_name, node_port, jwt)
            # Deploy mysql cluster without backup
            print("Deploying your cluster...")
            # helm_chart_path
            command = f"helm install {cluster_name} {helm_chart_path} \
--set replicas={replica} \
--set rootPassword={root_password} \
--set mysqlnodeport={node_port} \
--set volumeSpec.persistentVolumeClaim.resources.requests.storage={pvc_size}Gi"
            output = os.popen(command).read()
            print(output)
            print("Please wait until the cluster becomes ready...")
            print(f"Access your cluster with port {node_port} \n")
        else:
            print("Please enter yes or no.")


def create_cluster_from_backup():
    print('Create Cluster from existing backup')
    jwt = input("JWT: ")
    # ex: cloud.gig.tech/api/1
    api_url = input("API URL: ")
    customer_id = input("Customer ID: ")
    cloudspace_id = input("CloudSpace ID: ")
    cluster_name = input("Cluster Name: ")
    replica = input("Number of replicas: ")
    # use your root password from backup
    root_password = input("Root Password:  ")
    node_port = int(input("MySQL NodePort [30000-32767]: "))
    pvc_size = input("Cluster Size (Gi): ")
    list_backups()
    backup_number = int(input("Enter your backup number: "))
    backup_file_name = mydict[backup_number]
    print(f"You select {backup_file_name}")
    backup_bucket_url = f's3://{mybucket}/{backup_file_name}'
    s3_url = s3_endpoint
    # DEF CREATE SERVER POOL & LB
    create_server_pool_lb(api_url, customer_id, cloudspace_id,
                          cluster_name, node_port, jwt)
    # Deploy your cluster ..
    print("Deploying your cluster...")
    # helm_chart_path
    command = f'helm install {cluster_name} {helm_chart_path} \
--set replicas={replica} --set rootPassword={root_password} \
--set mysqlnodeport={node_port} \
--set initBucketURL={backup_bucket_url} \
--set backupCredentials.AWS_ACCESS_KEY_ID="{s3_access_key}" \
--set backupCredentials.AWS_SECRET_ACCESS_KEY="{s3_secret_key}" \
--set backupCredentials.S3_PROVIDER=Minio \
--set backupCredentials.S3_ENDPOINT=https://{s3_url} \
--set volumeSpec.persistentVolumeClaim.resources.requests.storage={pvc_size}Gi'
    output = os.popen(command).read()
    print(output)
    print("Please wait until the cluster becomes ready...")
    print(f"Access your cluster with port {node_port}")


def edit_cluster():
    print('Edit your cluster')
    cluster_name = input("Cluster Name: ")
    while(True):
        print_edit_cluster_menu()
        option = ''
        try:
            option = int(input('Choice: '))
        except Exception:
            print('Wrong input. Please enter a number ...')
        # Check what choice was entered and act accordingly
        if option == 1:
            replica_num = input("Number of replicas:")
            command = f'kubectl scale --replicas={replica_num}\
                        mysqlcluster {cluster_name}'
            output = os.popen(command).read()
            print(output)
            break
        elif option == 2:
            get_cluster_yaml = f'kubectl get mysqlcluster {cluster_name}\
                                 -o yaml > {cluster_name}.yaml '
            output = os.popen(get_cluster_yaml).read()
            cronjob_input = input("Custom Cronjob:")
            cronjob = f"'{cronjob_input}'"
            # replace cronjob
            replace_cronjob = f'sed -i "s/backupSchedule.*/backupSchedule: {cronjob}/g"\
                                {cluster_name}.yaml'
            output = os.popen(replace_cronjob).read()
            apply_changes = f'kubectl apply -f {cluster_name}.yaml'
            output = os.popen(apply_changes).read()
            print(output)
            break
        else:
            print('Invalid option. Please enter a number between 1 and 2.')


def list_clusters():
    print("List clusters....")
    list_helm_deployment = 'helm list -A '
    output = os.popen(list_helm_deployment).read()
    mylist = []
    for line in output.splitlines():
        fields = line.split()
        # Save output to list
        mylist.append(fields)
    # Remove first row
    mylist.remove(mylist[0])

    # print list line by line with grep cluster-0.3.1
    for line in mylist:
        chart_name = line[8]
        # check if chart equal to cluster-0.3.1 "Grep"
        if chart_name == "cluster-0.3.1":
            # save first column to deployment_name
            deployment_name = line[0]

            print(f'\n helm deployment name: {deployment_name}')
            list_deployment_resources = f'helm get all {deployment_name}'

            output = os.popen(list_deployment_resources).read()

            for line in output.splitlines():
                if "nodePort:" in line:
                    print(f' Port: {line.split()[2]}')
                if "mysql.presslabs.org/cluster" in line:
                    print(f' Cluster Name: {line.split()[1]}')


def remove_cluster():
    list_helm_deployment = 'helm list -A '
    output = os.popen(list_helm_deployment).read()
    mylist = []
    for line in output.splitlines():
        fields = line.split()
        # Save output to list
        mylist.append(fields)
    # Remove first row
    mylist.remove(mylist[0])

    # print list line by line with grep cluster-0.3.1
    for line in mylist:
        chart_name = line[8]
        # check if chart equal to cluster-0.3.1 "Grep"
        if chart_name == "cluster-0.3.1":
            # print first column
            print(line[0])

    deployment_name = input("Deployment Name to be remove: ")
    if input("are you sure to delete? (y/n) ") != "y":
        exit()
    delete_deployment = f'helm delete {deployment_name}'
    output = os.popen(delete_deployment).read()
    print(output)


def list_backups():
    print('List Backups from Object Storage...')
    global mybucket, s3_endpoint, s3_port, s3_access_key, s3_secret_key
    s3_endpoint = input("Object storage endpoint: ")
    s3_port = input("Object storage port: ")
    s3_access_key = input("Object storage access key: ")
    s3_secret_key = input("Object storage secret key: ")
    mybucket = input("Bucket Name: ")
    endpoint_url = f"{s3_endpoint}:{s3_port}"
    s3_access = f"{s3_access_key}"
    s3_secret = f"{s3_secret_key}"
    test_s3_connection(s3_endpoint, s3_port, s3_access_key, s3_secret_key)

    client = Minio(
        endpoint=endpoint_url,
        secure=True,
        access_key=s3_access,
        secret_key=s3_secret
    )
    index = 0  # start index with 0
    global mydict
    mydict = {}  # empty dic
    # List Objects
    objects = client.list_objects(mybucket, prefix=None, recursive=True)
    for obj in objects:
        # Save index and file backup name
        backup_list = f"{index} - {obj.object_name} "
        # save backup files to dics to list them by index in futuer xD
        mydict[index] = obj.object_name
        # Print index, file backup name
        print(backup_list)
        index += 1


def main():
    while(True):
        print_menu()
        option = ''
        try:
            option = int(input('Enter your choice: '))
        except Exception:
            print('Wrong input. Please enter a number ...')
        # Check what choice was entered and act accordingly
        if option == 1:
            install_mysql_operator()
        elif option == 2:
            create_cluster()
        elif option == 3:
            create_cluster_from_backup()
        elif option == 4:
            list_clusters()
        elif option == 5:
            edit_cluster()
        elif option == 6:
            remove_cluster()
        elif option == 7:
            list_backups()
        elif option == 8:
            print('Thanks for using our service')
            exit()
        else:
            print('Invalid option. Please enter a number between 1 and 8.')
