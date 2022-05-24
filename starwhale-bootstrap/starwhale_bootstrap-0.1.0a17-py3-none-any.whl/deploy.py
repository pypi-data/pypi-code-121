import os

import ansible_runner


def deploy(logdir: str = "",
           extravars: dict = {},
           cmdline: str = "",
           inventory: dict = {}):
    cur_path = os.path.abspath(os.path.dirname(__file__))
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    # for issue https://github.com/ansible/ansible-runner/issues/853
    os.chmod(logdir+'/inventory/hosts.json', 0o600)
    # ABSPATH = '/mnt/c/Users/gaoxinxing/IdeaProjects/containerdJavaGrpc/bootstrap/'
    # 可参考：https://gist.github.com/privateip/879683a0172415c408fb2afb82a97511

    r = ansible_runner.run(
        private_data_dir=logdir,
        playbook=cur_path + '/playbook/bootstrap.yaml',
        roles_path=cur_path + '/playbook/roles',
        extravars=extravars,
        cmdline=cmdline,
        # 来源：https://ansible.leops.cn/advanced/dynamic-hosts/
        inventory=inventory
        # optional
        # ssh_key='',
    )

    os.chmod(logdir+'/inventory/hosts.json', 0o600)
    print("{}: {}".format(r.status, r.rc))
    # successful: 0
    for each_host_event in r.events:
        print(each_host_event['event'])
    print("Final status:")
    print(r.stats)
