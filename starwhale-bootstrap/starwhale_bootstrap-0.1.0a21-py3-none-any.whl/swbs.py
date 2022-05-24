import os

import ansible_runner

#
# # base
# base_root_path = '/mnt/data/starwhale-b'
# sw_version = 'latest'
# sw_repository = 'starwhaleai'  # or else ghcr.io/star-whale
#
# # mysql
# mysql_image = 'mysql:8.0-debian'
# mysql_port = '3406'
# mysql_root_pwd = 'starwhale'
# mysql_data_dir = base_root_path + '/local-storage-mysql'
#
# # minio
# minio_image = 'quay.io/minio/minio'
# minio_data_dir = base_root_path + '/local-storage'
# minio_default_bucket = 'starwhale'
# minio_access_key = 'minioadmin'
# minio_secret_key = 'minioadmin'
# # todo the same node can't deploy multi minio instance even different port(because other port can't effect)
# # reason: minio docker file expose fixed port
# minio_server_port = 9000
# minio_console_port = 9001
#
# # controller variables
# controller_image = base_root_path + '/server:' + sw_version
# controller_task_split_num = '2'
# controller_port = '8182'
#
# # agent variables
# # agent
# agent_image = base_root_path + '/server:' + sw_version
# # task storage dir
# agent_data_dir = base_root_path + '/agent/run'
# # pypi url
# pypi_index_url = 'http://10.131.0.1:3141/root/pypi-douban/+simple/'
# # pypi extra url
# pypi_extra_index_url = 'https://pypi.tuna.tsinghua.edu.cn/simple/'
# # pypi trusted host
# pypi_trusted_host = '10.131.0.1 pypi.tuna.tsinghua.edu.cn'
#
# # taskset
# taskset_image = '{{ sw_repository }}/taskset:' + sw_version
# taskset_docker_port = '2676'
# taskset_dind_dir = base_root_path + '/agent/dind'

config = {
    # base
    'base_root_path': '/mnt/data/starwhale-b',
    'sw_version': 'latest',
    'sw_repository': 'starwhaleai',  # or else ghcr.io/star-whale

    # mysql
    'mysql_image': 'mysql:8.0-debian',
    'mysql_port': '3406',
    'mysql_root_pwd': 'starwhale',
    'mysql_data_dir': '{{ base_root_path }}/local-storage-mysql',

    # minio
    'minio_image': 'quay.io/minio/minio',
    'minio_data_dir': '{{ base_root_path }}/local-storage',
    'minio_default_bucket': 'starwhale',
    'minio_access_key': 'minioadmin',
    'minio_secret_key': 'minioadmin',
    # reason: minio docker file expose fixed port
    'minio_server_port': '9000',
    'minio_console_port': '9001',

    # controller variables
    'controller_image': '{{ sw_repository }}/server:{{ sw_version }}',
    'controller_task_split_num': '2',
    'controller_port': '8182',

    # agent variables
    # agent
    'agent_image': '{{ sw_repository }}/server:{{ sw_version }}',
    # task storage dir
    'agent_data_dir': '{{ base_root_path }}/agent/run',
    # pypi url
    'pypi_index_url': 'http://10.131.0.1:3141/root/pypi-douban/+simple/',
    # pypi extra url
    'pypi_extra_index_url': 'https://pypi.tuna.tsinghua.edu.cn/simple/',
    # pypi trusted host
    'pypi_trusted_host': '10.131.0.1 pypi.tuna.tsinghua.edu.cn',

    # taskset
    'taskset_image': '{{ sw_repository }}/taskset:{{ sw_version }}',
    'taskset_docker_port': '2676',
    'taskset_dind_dir': '{{ base_root_path }}/agent/dind'
}


def deploy():
    # todo tmp
    cur_path = os.path.abspath(os.path.dirname(__file__))
    # ABSPATH = '/mnt/c/Users/gaoxinxing/IdeaProjects/containerdJavaGrpc/bootstrap/'
    # 可参考：https://gist.github.com/privateip/879683a0172415c408fb2afb82a97511
    r = ansible_runner.run(
        private_data_dir='/var/starwhale/tmp',
        playbook=cur_path + '/playbook/bootstrap.yaml',
        roles_path=cur_path + '/playbook/roles',
        extravars={
            # base
            'base_root_path': '/mnt/data/starwhale-b',
            'sw_version': 'latest',
            'sw_repository': 'starwhaleai',  # or else ghcr.io/star-whale

            # mysql
            'mysql_image': 'mysql:8.0-debian',
            'mysql_port': '3406',
            'mysql_root_pwd': 'starwhale',
            'mysql_data_dir': '{{ base_root_path }}/local-storage-mysql',

            # minio
            'minio_image': 'quay.io/minio/minio',
            'minio_data_dir': '/mnt/data/starwhale-b/local-storage',
            'minio_default_bucket': 'starwhale',
            'minio_access_key': 'minioadmin',
            'minio_secret_key': 'minioadmin',
            # reason: minio docker file expose fixed port
            'minio_server_port': '9000',
            'minio_console_port': '9001',

            # controller variables
            'controller_image': '{{ sw_repository }}/server:{{ sw_version }}',
            'controller_task_split_num': '2',
            'controller_port': '8182',

            # agent variables
            # agent
            'agent_image': '{{ sw_repository }}/server:{{ sw_version }}',
            # task storage dir
            'agent_data_dir': '{{ base_root_path }}/agent/run',
            # pypi url
            'pypi_index_url': 'http://10.131.0.1:3141/root/pypi-douban/+simple/',
            # pypi extra url
            'pypi_extra_index_url': 'https://pypi.tuna.tsinghua.edu.cn/simple/',
            # pypi trusted host
            'pypi_trusted_host': '10.131.0.1 pypi.tuna.tsinghua.edu.cn',

            # taskset
            'taskset_image': '{{ sw_repository }}/taskset:{{ sw_version }}',
            'taskset_docker_port': '2676',
            'taskset_dind_dir': '{{ base_root_path }}/agent/dind'
        },
        cmdline='--user gaoxinxing',
        # 来源：https://ansible.leops.cn/advanced/dynamic-hosts/
        inventory={
            "controller": {"hosts": {"controller.starwhale.com": {}}},
            "storage": {"hosts": {"storage.starwhale.com": {}}},
            "agent": {
                "hosts": {
                    "agent01.starwhale.com": {},
                    "agent02.starwhale.com": {},
                    "agent03.starwhale.com": {},
                    "agent04.starwhale.com": {}
                }
            }
        }
        # optional
        # ssh_key='',
    )
    print("{}: {}".format(r.status, r.rc))
    # successful: 0
    for each_host_event in r.events:
        print(each_host_event['event'])
    print("Final status:")
    print(r.stats)

# run ansible/generic commands in interactive mode within container
# out, err, rc = ansible_runner.run_command(
#     executable_cmd='ansible-playbook',
#     cmdline_args=['/mnt/c/Users/gaoxinxing/IdeaProjects/containerdJavaGrpc/bootstrap/bootstrap.yaml',
#                   '-i', '/mnt/c/Users/gaoxinxing/IdeaProjects/containerdJavaGrpc/bootstrap/hosts',
#                   '--user', 'gaoxinxing', '-vvvv'],
#     input_fd=sys.stdin,
#     output_fd=sys.stdout,
#     error_fd=sys.stderr
# )
# print("rc: {}".format(rc))
# print("out: {}".format(out))
# print("err: {}".format(err))
