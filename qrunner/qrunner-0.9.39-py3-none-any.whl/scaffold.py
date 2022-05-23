import os.path
import sys

api_run_content = """import qrunner


if __name__ == '__main__':
    qrunner.main(
        platform='api',
        base_url='https://www.qizhidao.com'
    )
"""

android_run_content = """import qrunner


if __name__ == '__main__':
    qrunner.main(
        platform='android',
        serial_no='UJK0220521066836',
        pkg_name='com.qizhidao.clientapp'
    )
"""

ios_run_content = """import qrunner


if __name__ == '__main__':
    qrunner.main(
        platform='ios',
        serial_no='00008101-000E646A3C29003A',
        pkg_name='com.qizhidao.company'
    )
"""

browser_run_content = """import qrunner


if __name__ == '__main__':
    qrunner.main(
        platform='web',
        base_url='https://patents-pre.qizhidao.com'
    )
"""

case_content_android = """import qrunner


@qrunner.story('首页')
class TestAdrSample(qrunner.TestCase):
    
    @qrunner.title('从首页进入我的页')
    def test_go_my(self):
        self.click(resourceId='id/bottom_btn', desc='广告关闭按钮')
        self.click(resourceId='id/bottom_view', index=3, desc='底部导航-我的')
        self.assertText('我的订单', desc='我的订单标题')
"""

case_content_ios = """import qrunner


@qrunner.story('首页')
class TestIosSample(qrunner.TestCase):

    @qrunner.title('从首页进入我的页')
    def test_go_my(self):
        self.click(label='我的', desc='底部导航-我的')
        self.assertText('我的订单', desc='我的订单标题')
"""

case_content_web = """import qrunner


@qrunner.story('专利检索')
class TestWebSample(qrunner.TestCase):
    
    @qrunner.title('专利简单检索')
    def test_patent_search(self):
        self.open_url('https://patents-pre.qizhidao.com/', desc='专利首页')
        self.set_text('无人机', xpath='//*[@id="driver-home-step1"]', desc='专利搜索框')
        self.click(id_='driver-home-step2', desc='搜索按钮')
        self.assertTitle('无人机专利检索-企知道', desc='专利搜索页')
"""

case_content_api = """import qrunner


@qrunner.story('PC站首页')
class TestApiSample(qrunner.TestCase):

    @qrunner.title('查询PC站首页banner列表')
    @qrunner.file_data('card_type', 'data.json')
    def test_getToolCardListForPc(self, card_type):
        path = '/api/qzd-bff-app/qzd/v1/home/getToolCardListForPc'
        pay_load = {"type": card_type}
        self.post(path, json=pay_load)
        self.assertEq('code', 0)
"""

require_content = """qrunner
"""

ignore_content = "\n".join(
    ["__pycache__/*", "*.pyc", ".idea/*", ".DS_Store", "allure-results", "report"]
)

data_content = """{
  "card_type": [0, 1, 2]
}
"""


def init_scaffold_project(subparsers):
    parser = subparsers.add_parser("start", help="Create a new project with template structure.")
    parser.add_argument('-t', '--platform', dest='platform', type=str, default='api', help='测试平台: api、android、ios、web')
    return parser


def create_scaffold(platform):
    """ create scaffold with specified project name.
    """

    def create_folder(path):
        os.makedirs(path)
        msg = f"created folder: {path}"
        print(msg)

    def create_file(path, file_content=""):
        with open(path, "w", encoding="utf-8") as f:
            f.write(file_content)
        msg = f"created file: {path}"
        print(msg)

    project_name = f'{platform}_demo'
    create_folder(project_name)
    create_file(
        os.path.join(project_name, ".gitignore"),
        ignore_content,
    )
    create_file(
        os.path.join(project_name, "requirements.txt"),
        require_content,
    )
    create_folder(os.path.join(project_name, 'test_dir'))
    create_file(
        os.path.join(project_name, 'test_dir', "__init__.py"),
        '',
    )
    if platform == 'api':
        create_file(
            os.path.join(project_name, "run.py"),
            api_run_content,
        )
        create_file(
            os.path.join(project_name, 'test_dir', "test_api_sample.py"),
            case_content_api,
        )
    elif platform == 'android':
        create_file(
            os.path.join(project_name, "run.py"),
            android_run_content,
        )
        create_file(
            os.path.join(project_name, 'test_dir', "test_adr_sample.py"),
            case_content_android,
        )
    elif platform == 'ios':
        create_file(
            os.path.join(project_name, "run.py"),
            ios_run_content,
        )
        create_file(
            os.path.join(project_name, 'test_dir', "test_ios_sample.py"),
            case_content_ios,
        )
    elif platform == 'web':
        create_file(
            os.path.join(project_name, "run.py"),
            browser_run_content,
        )
        create_file(
            os.path.join(project_name, 'test_dir', "test_web_sample.py"),
            case_content_web,
        )
    else:
        print(f'不支持的平台: {platform}')
        sys.exit()
    create_folder(os.path.join(project_name, 'test_data'))
    create_file(
        os.path.join(project_name, 'test_data', "data.json"),
        data_content,
    )
    create_folder(os.path.join(project_name, 'report'))
    return 0


def main_scaffold_project(args):
    sys.exit(create_scaffold(args.platform))

