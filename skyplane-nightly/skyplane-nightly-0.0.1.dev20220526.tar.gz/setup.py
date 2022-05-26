# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['skyplane',
 'skyplane.cli',
 'skyplane.cli.cli_impl',
 'skyplane.cli.experiments',
 'skyplane.compute',
 'skyplane.compute.aws',
 'skyplane.compute.azure',
 'skyplane.compute.gcp',
 'skyplane.gateway',
 'skyplane.obj_store',
 'skyplane.replicate',
 'skyplane.utils']

package_data = \
{'': ['*']}

install_requires = \
['awscrt>=0.13.11,<0.14.0',
 'azure-identity>=1.10.0,<2.0.0',
 'azure-mgmt-authorization>=2.0.0,<3.0.0',
 'azure-mgmt-compute>=27.0.0,<28.0.0',
 'azure-mgmt-network>=20.0.0,<21.0.0',
 'azure-mgmt-resource>=21.1.0,<22.0.0',
 'azure-mgmt-storage>=20.0.0,<21.0.0',
 'azure-storage-blob>=12.0.0',
 'boto3>=1.23.5,<2.0.0',
 'cachetools>=5.1.0,<6.0.0',
 'click>=8.1.3,<9.0.0',
 'google-api-python-client>=2.48.0,<3.0.0',
 'google-auth>=2.6.6,<3.0.0',
 'google-cloud-compute>=1.3.1,<2.0.0',
 'google-cloud-storage>=2.3.0,<3.0.0',
 'grpcio-status>=1.33.2',
 'halo>=0.0.31,<0.0.32',
 'ilock>=1.0.3,<2.0.0',
 'pandas>=1.3,<2.0',
 'paramiko>=2.11.0,<3.0.0',
 'questionary>=1.10.0,<2.0.0',
 'sshtunnel>=0.4.0,<0.5.0',
 'termcolor>=1.1.0,<2.0.0',
 'tqdm>=4.64.0,<5.0.0',
 'typer>=0.4.1,<0.5.0']

extras_require = \
{'gateway': ['lz4>=4.0.0,<5.0.0',
             'flask>=2.1.2,<3.0.0',
             'pyopenssl>=22.0.0,<23.0.0',
             'werkzeug>=2.1.2,<3.0.0'],
 'solver': ['cvxopt>=1.3.0,<2.0.0',
            'cvxpy>=1.2.1,<2.0.0',
            'graphviz>=0.20,<0.21',
            'matplotlib>=3.5.2,<4.0.0',
            'numpy>=1.21.0,<2.0.0']}

entry_points = \
{'console_scripts': ['skylark = skyplane.cli.cli:app',
                     'skyplane = skyplane.cli.cli:app']}

setup_kwargs = {
    'name': 'skyplane-nightly',
    'version': '0.0.1.dev20220526',
    'description': 'Skyplane efficiently transports data between cloud regions and providers.',
    'long_description': '# Skyplane: A Unified Data Layer for the Multi-Cloud\n\n\n[![Docker](https://github.com/skyplane-project/skyplane/actions/workflows/docker-publish.yml/badge.svg?branch=main)](https://github.com/skyplane-project/skyplane/actions/workflows/docker-publish.yml)\n\n<img src="https://gist.githubusercontent.com/parasj/d67e6e161ea1329d4509c69bc3325dcb/raw/232009efdeb8620d2acb91aec111dedf98fdae18/skylark.jpg" width="200px">\n\nSkyplane is lifting cloud object stores to the Sky.\n\n## Instructions to build and run demo\nSkyplane is composed of two components: A ReplicatorClient that runs locally on your machine that is responsible for provisioning instances and coordinating replication jobs and a GatewayDaemon that runs on each provisioned instance to actually copy data through the overlay.\n\nThis package represents both components as a single binary. Docker builds a single container with the GatewayDaemon and pushes it to the Github Container Registry (ghcr.io). After provisioning an instance, a GatewayDaemon is started by launching that container. Therefore, it\'s simple and fast to launch a new Gateway.\n\n### Requirements\n* Python 3.7 or greater\n* Docker\n    * **Ensure you have authenticated your Github account with Docker**: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-to-the-container-registry\n    * TLDR:\n        * (1) Install docker with `curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh`\n        * (2) Create a Personal Access Token at https://github.com/settings/tokens/new with "write:packages" permissions\n        * (3) Run `echo <PERSONAL_ACCESS_TOKEN> | sudo docker login ghcr.io -u <GITHUB_USERNAME> --password-stdin`\n* AWS:\n\t* (1) Install AWS CLI with `sudo apt install awscli`\n\t* (2) Configure AWS by running `aws configure` and input the necessary information. See https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html. \n\t* (3) Ensure that you have a sufficient AWS vCPU limit in any regions you intend to use\n\t* (4) Install netcat with `sudo apt install netcat`\n\n### Building and deploying the gateway\n\nFirst, clone and enter the skyplane directory:\n```\n$ git clone https://github.com/skyplane-project/skyplane\n$ cd skyplane\n```\n\nThen, configure cloud credentials as needed:\n\n* AWS: `aws configure`\n* GCS: `gcloud auth application-default login`\n* Azure: `az login`\n\nFinally, install and initalize Skyplane:\n```\n$ pip install -e ".[all]"\n$ skyplane init\n```\n\nTo run a sample transfer, first build a new version of the GatewayDaemon Docker image and push it to ghcr.io (ensure you are authenticated as above):\n```\n$ source scripts/pack_docker.sh\n```\n<details>\n<summary>pack_docker result</summary>\n<br>\n\n```\n$ pip install -e ".[all]"\n$ source scripts/pack_docker.sh\nBuilding docker image\n[+] Building 0.0s (2/2) FINISHED\n => [internal] load build definition from Dockerfile                                                                                               0.0s\n => => transferring dockerfile: 2B                                                                                                                 0.0s\n => [internal] load .dockerignore                                                                                                                  0.0s\n => => transferring context: 2B                                                                                                                    0.0s\nfailed to solve with frontend dockerfile.v0: failed to read dockerfile: open /var/lib/docker/tmp/buildkit-mount683951637/Dockerfile: no such file or directory\nUploading docker image to ghcr.io/skyplane-project/skyplane:local-PotRzrFT\nThe push refers to repository [ghcr.io/skyplane-project/skyplane]\n20d2ed8618ca: Layer already exists\n1c4146875228: Layer already exists\n1f4f7ac2f199: Layer already exists\nd1e36ec88afa: Layer already exists\n824bf068fd3d: Layer already exists\nlocal-PotRzrFT: digest: sha256:f412e376290d5a7bad28aca57ce9ffcf579e8dd7db3f4d6fb68ceae829d0a6b2 size: 1371\nDeleted build cache objects:\ntltkismwtov5n8zokghil1py9\nu0e2ymhmv64oriiq66ibepn63\n\nTotal reclaimed space: 0B\nSKYPLANE_DOCKER_IMAGE=ghcr.io/skyplane-project/skyplane:local-PotRzrFT\n```\n\n</details>\n\nThe script will export the new image (ghcr.io/skyplane-project/skyplane:local-PotRzrFT in this example) to an environment variable (`SKYPLANE_DOCKER_IMAGE`). Ensure you use `source` so the environment variable is published to your shell.\n\n### Running a basic cloud to cloud transfer job\nWe then run the ReplicatorClient with that new Docker image (stored in `$SKYPLANE_DOCKER_IMAGE`):\n```\n$ skyplane cp [s3/gs/azure]://[source-bucket-name]/[source-key-prefix] [s3/gs/azure]://[dest-bucket-name]/[dest-key-prefix]\n```\n<details>\n<summary>skyplane cp result</summary>\n<br>\n \n```\n$ skyplane cp s3://skyplane-example-us-east-1/ s3://skyplane-example-us-west-1/\n11:34:48 [DEBUG] Cloud SSH key initialization: 3.23s\n11:35:20 [DEBUG] Provisioning instances and waiting to boot: 31.87s\n11:35:24 [DEBUG] Install docker: 2.79s\n11:35:24 [DEBUG] Install docker: 2.50s\n11:35:37 [DEBUG] Starting gateway aws:us-west-1:i-09dda9567bcf9ecad, host: 52.53.229.126: Docker pull: 13.10s\n11:35:37 [DEBUG] Starting gateway aws:us-west-1:i-09dda9567bcf9ecad, host: 52.53.229.126: Starting gateway container\n11:35:39 [DEBUG] Starting gateway aws:us-west-1:i-09dda9567bcf9ecad, host: 52.53.229.126: Gateway started fabfc1cd5aefa24c0cb5d5572501b19ff33e483cadfcccddc9bd0d90368c5329\n11:36:05 [DEBUG] Starting gateway aws:us-east-1:i-08a9b4f70ee2caca3, host: 54.158.252.172: Docker pull: 39.93s\n11:36:05 [DEBUG] Starting gateway aws:us-east-1:i-08a9b4f70ee2caca3, host: 54.158.252.172: Starting gateway container\n11:36:14 [DEBUG] Starting gateway aws:us-east-1:i-08a9b4f70ee2caca3, host: 54.158.252.172: Gateway started 18ebc8a3a04b632375a71ae88e18286d402364e467b30b00ad3168391a914eaf\n11:36:15 [DEBUG] Install gateway package on instances: 55.05s\n11:36:15 [INFO]  Provisioned ReplicationTopologyGateway(region=\'aws:us-east-1\', instance=0): http://54.158.252.172:8888/container/18ebc8a3a04b\n11:36:15 [INFO]  Provisioned ReplicationTopologyGateway(region=\'aws:us-west-1\', instance=0): http://52.53.229.126:8888/container/fabfc1cd5aef\n11:36:15 [INFO]  Batch 0 size: 4387690 with 3 chunks\n11:36:15 [DEBUG] Building chunk requests: 0.00s\n11:36:15 [DEBUG] Sending 3 chunk requests to 54.158.252.172\n11:36:15 [DEBUG] Dispatch chunk requests: 0.27s\n11:36:15 [INFO]  0.00GByte replication job launched\n0/3 chunks done (0.00 / 0.00GB, 0.00Gbit/s, ETA=unknown)                                                                                                    \nReplication: average 0.02Gbit/s: 100%|███████████████████████████████████████████████████████████████████████████████| 33.5M/33.5M [00:02<00:00, 17.0Mbit/s]\n11:36:17 [INFO]  Copying gateway logs from aws:us-east-1:i-08a9b4f70ee2caca3\n11:36:17 [INFO]  Copying gateway logs from aws:us-west-1:i-09dda9567bcf9ecad\n11:36:21 [DEBUG] Wrote profile to /tmp/skyplane/transfer_2022-03-29T11:36:17.755039/traceevent_5cb6dfbf-fac6-4ce6-a61b-1b813e83723d.json, visualize using `about://tracing` in Chrome\n11:36:22 [WARN]  Deprovisioning 2 instances\n11:36:23 [WARN]  Deprovisioned aws:us-west-1:i-09dda9567bcf9ecad\n11:36:24 [WARN]  Deprovisioned aws:us-east-1:i-08a9b4f70ee2caca3\n\n{"total_runtime_s": 1.692787, "throughput_gbits": 0.019311843710588934, "monitor_status": "completed", "success": true}\n```\n\n</details>\n\nWhen done, stop all instances started by Skyplane by running:\n\n```skyklark deprovision```\n\n<details>\n<summary>skyplane deprovision result</summary>\n<br>\n\n```\n$ skyplane deprovision\nNo GCP project ID given, so will only deprovision AWS instances\nDeprovisioning 3 instances\nDeprovisioning (aws:ap-northeast-1): 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 3/3 [00:01<00:00,  2.33it/s]\n```\n\n</details>\n',
    'author': 'Skyplane authors',
    'author_email': 'skyplaneproject@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/skyplane-project/skyplane',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
