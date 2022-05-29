import os

# constants
DOCKER_REGISTRY = os.getenv("FABRIQUE_DOCKER_REGISTRY", '10.166.48.4:52525')
CORE_IMG_NAME = os.getenv('FABRIQUE_CORE_IMG_NAME',  'python:3.6-centos-krb5-43')


class FabriqueDockerfile:
    def __init__(self, dockerfile_text=None,
                 fabrique_image_name=f'{DOCKER_REGISTRY}/{CORE_IMG_NAME}',
                 pipeline_pth='',
                 requirements=True,
                 run_params='', custom_strings=''):

        self.dockerfile_text = dockerfile_text
        self.fabrique_image_name = fabrique_image_name
        self.requirements = requirements
        assert pipeline_pth
        self.pipeline_pth = pipeline_pth
        self.custom_strings = custom_strings
        self.run_params = run_params

    def render(self):
        if self.dockerfile_text:
            return self.dockerfile_text

        df_text = ''

        assert self.fabrique_image_name
        print(self.fabrique_image_name)

        df_text += f"FROM {self.fabrique_image_name}\n"
        df_text += 'RUN mkdir /opt/app\n'
        df_text += 'RUN python3 -m pip install fabrique-actor\n'

        if self.requirements:
            df_text += 'COPY requirements.txt /opt/app\n'

            fpath = os.path.join(self.pipeline_pth, 'requirements.txt')
            res_fpath = '/opt/app/requirements.txt'
            whl_dir = os.path.join(self.pipeline_pth, 'wheelhouse')
            res_whl_dir = '/opt/app/wheelhouse'
            if os.path.isfile(fpath):
                if os.path.isdir(whl_dir):
                    df_text += f'RUN python3 -m pip install --no-index --find-links={res_whl_dir} -r {res_fpath}\n'
                else:
                    df_text += f'RUN python3 -m pip install -r {res_fpath}\n'


        df_text += 'COPY . /opt/app\n'
        df_text += 'WORKDIR /opt/app\n'

        if self.custom_strings:
            df_text += self.custom_strings
        if self.run_params:
            df_text += self.run_params

        return df_text

    def write(self, df_text, df_dir=None):
        if not df_dir:
            df_dir = self.pipeline_pth

        fpath = os.path.join(df_dir, 'Dockerfile')

        if os.path.isfile(fpath):
            print('Dockerfile already exists')
            return

        with open(fpath, 'w') as f:
            f.write(df_text)

    def render_and_write(self):
        self.write(self.render())
        print(f'Dockerfile is generated in {self.pipeline_pth}')
