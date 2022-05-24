from polidoro_argument import Command

from polidoro_cli import CLI


class Kubectl(CLI):
    @staticmethod
    def _get_pod_name(pod_name):
        pod = Kubectl.pod_names(pod_name)
        if not pod:
            print(f'pod name "{pod_name}" not found!')
            exit(1)
        return pod.split()[0]

    @staticmethod
    @Command(
        help='Return the pod names',
        aliases=['e']
    )
    def pod_names(filter=''):
        pods, err = Kubectl.execute(
            'get pods -o=custom-columns=NAME:.metadata.name --field-selector=status.phase=Running',
            capture_output=True,
            show_cmd=False,
            include_default_command=True
        )
        if filter:
            pods = '\n'.join(p for p in pods.split() if filter in p)
        return pods

    @staticmethod
    @Command(
        help='Run "exec" in the pod',
        aliases=['b']
    )
    def exec(pod_name, *remainders):
        Kubectl.execute(f'exec -it {Kubectl._get_pod_name(pod_name)} -- {" ".join(remainders)}', include_default_command=True)

    @staticmethod
    @Command(
        help='Run "logs -f" in the pod',
        aliases=['l']
    )
    def logs(pod_name):
        Kubectl.execute(f'logs {Kubectl._get_pod_name(pod_name)} -f', include_default_command=True)
