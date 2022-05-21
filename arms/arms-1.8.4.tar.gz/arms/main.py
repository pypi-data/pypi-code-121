import os
import sys
import shutil
from lesscli import add_argument, add_subcommand, run
import re
import json
import random
from arms.utils.wordstyle import replace_dict, replace_all, WordStyle, WordSeed
from arms.utils.common import dump_file_name
from arms.designer import run_design
from arms.codegen import run_codegen
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt


console = Console()


def alert_and_exit(text):
    console.print(text.replace('[', '\\['), style="bold red")
    exit(1)


def terminal_menu(options, show_func):
    """
    :param options: 选项列表
    :param show_func: 从选项获取描述的函数
    :return: 选中的选项，None表示退出
    """
    page_no = 0
    page_size = 9
    total_page = (len(options) - 1) // 9 + 1
    while True:
        opt_slide = options[page_no * page_size: (page_no + 1) * page_size]
        panel_lines = []
        for idx, opt_item in enumerate(opt_slide):
            panel_lines.append('[bold][%d][/bold] < %s' % (idx + 1, show_func(opt_item)))
        panel_lines.append('')
        panel_lines.append('[bold]\\[q][/bold] < Quit.')
        if page_no > 0:
            panel_lines.append('[bold]\\[k][/bold] < Previous Page.')
        if (page_no + 1) * page_size < len(options):
            panel_lines.append('[bold]\\[j][/bold] < Next Page.')
        page_hint = '' if total_page <= 1 else '(%d/%d)' % (page_no + 1, total_page)
        panel = Panel.fit('\n'.join(panel_lines), title="Welcome to Terminal Menu%s" % page_hint)
        console.print(panel)
        print('\nChoice: ', end='')
        try:
            os.system('/bin/stty raw')
            c = sys.stdin.read(1).lower()
            print(c)
            print('\r')
        finally:
            os.system('/bin/stty cooked')
        if c == 'q':
            return None
        elif '1' <= c <= str(len(opt_slide)):
            return opt_slide[int(c) - 1]
        elif page_no > 0 and c == 'k':
            page_no -= 1
            continue
        elif (page_no + 1) * page_size < len(options) and c == 'j':
            page_no += 1
            continue
        else:
            console.print("Exception: Wrong Number, Please Try Again.\n", style="bold red")
            continue


def makedir(real_path):
    from pathlib import Path
    Path(real_path).mkdir(parents=True, exist_ok=True)


def print_version():
    """
    显示版本
    """
    from arms import __version__
    text = """
    arms version: {}

    """.format(__version__)
    print(text)


def run_process(tpl_name, is_patch=False):
    """
    项目初始化工具
    """
    # [1/7]判断本地有.git目录
    if not os.path.isdir('.git'):
        alert_and_exit('Please change workdir to top! or run "git init" first.')
    # [2/7]拉取模版项目
    local_path = Path.home() / '.arms_config.json'
    if not local_path.exists():
        alert_and_exit('请先执行arms config [git_url]')
    config_json = json.loads(local_path.open(encoding='utf-8').read())
    if '__default__' in config_json:
        config_json = config_json[config_json['__default__']]
    if tpl_name not in config_json:
        alert_and_exit('模版名称不存在！')
    ret = os.system('rm -rf .arms_tpl && git clone %s .arms_tpl' % config_json[tpl_name]['git_url'])
    if ret:
        exit(1)
    # [3/7]生成替换字典
    json_path = Path('.arms_tpl/.arms.json')
    if not json_path.is_file():
        alert_and_exit('No .arms.json found in source project!')
    index_json = {}
    try:
        index_json.update(json.loads(json_path.open().read()))
    except Exception as e:
        alert_and_exit('.arms.json is not valid JSON format!')
    # 支持层级选择
    while isinstance(index_json, dict) and '__name__' not in index_json:
        options = [{'key': key, 'value': value} for key, value in index_json.items()]
        opt_choice = terminal_menu(options, lambda x: x['key'].strip())
        if opt_choice is None:
            exit(0)
        index_json = opt_choice['value']
    if not isinstance(index_json, dict):
        alert_and_exit('.arms.json错误: 节点类型错误!')
    if '__only__' in index_json:
        if '__except__' in index_json:
            alert_and_exit('.arms.json错误: __only__和__except__不能同时定义!')
        if '__rename__' in index_json:
            alert_and_exit('.arms.json错误: __only__和__rename__不能同时定义!')
    if '__rename__' in index_json:
        if any(rule.count(':') != 1 for rule in index_json['__rename__']):
            alert_and_exit('.arms.json错误: __rename__不符合规范!')
    if not isinstance(index_json['__name__'], list):
        alert_and_exit('.arms.json错误: __name__不符合规范!')
    for name_config in index_json['__name__']:
        if not name_config.get('word'):
            alert_and_exit('.arms.json错误: __name__[]["word"]不能为空!')
        if not name_config.get('hint'):
            alert_and_exit('.arms.json错误: __name__[]["hint"]不能为空!')

    # [4/7]删除无用路径
    if index_json.get('__only__'):
        only_paths = [rule.split(':')[-1] for rule in index_json['__only__']]
        rename_rules = [rule for rule in index_json['__only__'] if ':' in rule]
    else:
        only_paths = ['.']
        rename_rules = index_json.get('__rename__', [])
    except_paths = index_json.get('__except__', [])
    tar_cmd = 'tar %s -czf ../.arms_tpl.tgz --exclude .git %s' % (
        ' '.join(f'--exclude {p}' for p in except_paths), ' '.join(only_paths))
    print(tar_cmd)
    os.system(' && '.join([
        'cd .arms_tpl',
        tar_cmd,
        'cd ..',
        'rm -rf .arms_tpl',
        'mkdir .arms_tpl',
        'cd .arms_tpl',
        'tar -zxf ../.arms_tpl.tgz',
        'rm -f ../.arms_tpl.tgz'
    ]))
    repl_dict_all = {}
    out_abs_path = os.path.abspath('.')
    for name_config in index_json['__name__']:
        old_proj_name = name_config['word']
        new_proj_name = Prompt.ask('请输入%s' % name_config['hint'], default=old_proj_name)
        if old_proj_name == new_proj_name:
            continue
        if WordSeed.of(old_proj_name).word_style == WordStyle.other:
            alert_and_exit("被替换的[%s]不是支持的单词或词组形式！" % old_proj_name)
        if WordSeed.of(new_proj_name).word_style == WordStyle.other:
            alert_and_exit("输入的[%s]不是支持的单词或词组形式！" % new_proj_name)
        # [5/7]文件重命名
        repl_dict = replace_dict(old_proj_name, new_proj_name)
        repl_dict_all.update(repl_dict)
        os.chdir(out_abs_path)
        os.chdir('.arms_tpl')  # 变换工作目录
        for item in rename_rules:
            to_path, from_path = item.split(':', 1)
            if Path(from_path).exists():  # 前面的重命名可能会影响后面的重命名
                os.rename(from_path, to_path)  # os.rename非常强大
        curpath = Path('.')
        for i in range(20):  # 替换路径中的项目代号，最大循环20轮
            touched = False
            renames = []
            for p in curpath.rglob('*'):
                full_path = str(p)
                new_path = replace_all(full_path, repl_dict)
                if new_path != full_path:
                    renames.append(f'{new_path}:{full_path}')
            for item in renames:
                to_path, from_path = item.split(':', 1)
                if Path(from_path).exists():  # 前面的重命名可能会影响后面的重命名
                    os.rename(from_path, to_path)  # os.rename非常强大
                    touched = True
            if not touched:  # 若一轮操作没有产生重命名则退出
                break
        if is_patch:  # 通过重命名，保留重名文件
            midname = str(WordSeed(WordStyle.lower_snake, WordSeed.of(new_proj_name).tokens))
            out_path = Path('..')
            for p in curpath.rglob('*'):
                if p.is_file() and (out_path / p).is_file():
                    new_file_name = dump_file_name(p.parts[-1], project=midname)
                    p.rename('/'.join(p.parts[:-1] + (new_file_name,)))
        # [6/7]文本替换
        for p in curpath.rglob('*'):
            if p.is_dir() or str(p).startswith(('.git/', '.idea/', 'node_modules/')):
                continue
            try:
                text = p.open().read()
                new_text = replace_all(text, repl_dict)
                if new_text != text:
                    with p.open('w') as f:
                        f.write(new_text)
            except Exception as e:
                pass
    # [7/7]git add
    if not repl_dict_all:
        alert_and_exit("无文本替换，arms init已终止")
    console.print(Panel.fit(str(repl_dict_all), title='单词替换方案'))
    os.system('tar -czvf ../.arms_tpl.tgz .')
    os.chdir(out_abs_path)  # 变换工作目录
    os.system(' && '.join([
        'rm -rf .arms_tpl',
        'tar -zxf .arms_tpl.tgz',
        'rm -f .arms_tpl.tgz'
    ]))
    os.system('git add .')
    if is_patch:
        print('---- arms patch succeed :) ----')
    else:
        print('---- arms init succeed :) ----')


@add_argument('tpl_name', help='模版名')
def run_init(tpl_name):
    """
    项目初始化工具

    请输入命令完成项目初始化：arms init [tpl_name] （可先使用arms search [keyword]搜索模版名）
    """
    try:
        run_process(tpl_name=tpl_name, is_patch=False)
    except KeyboardInterrupt:
        print()
    finally:
        os.system('rm -rf .arms_tpl')
        os.system('rm -f .arms_tpl.tgz')


@add_argument('tpl_name', help='模版名')
def run_patch(tpl_name):
    """
    项目补丁工具
    arms patch [tpl_name]
    """
    try:
        run_process(tpl_name=tpl_name, is_patch=True)
    except KeyboardInterrupt:
        print()
    finally:
        os.system('rm -rf .arms_tpl')
        os.system('rm -f .arms_tpl.tgz')


def switch_config():
    local_path = Path.home() / '.arms_config.json'
    local_git_src = json.loads(local_path.open(encoding='utf-8').read())
    assert '__url__' not in local_git_src
    options = [key for key in local_git_src.keys() if key != '__default__']
    opt_choice = terminal_menu(options, lambda x: '(✔)' + x if x == local_git_src['__default__'] else '   ' + x)
    if opt_choice is None:
        exit(0)
    local_git_src['__default__'] = opt_choice
    with open(local_path, 'w') as f:
        f.write(json.dumps(local_git_src, ensure_ascii=False, indent=4))
    print("切换配置成功.")


def pull_config(git_url):
    # [1/2]拉取模版源
    ret = os.system("git clone %s .arms_tpl_src" % git_url)
    if ret:
        exit(1)
    # [2/2]保存到本地目录
    local_path = Path.home() / '.arms_config.json'
    try:
        try:
            local_git_src = json.loads(local_path.open(encoding='utf-8').read())
        except:
            local_git_src = {}
        if '__url__' in local_git_src:
            local_git_src = {local_git_src['__url__']: local_git_src}  #兼容老版本
        patch_git_src = json.loads(open('.arms_tpl_src/config.json').read())
        local_git_src[patch_git_src['__url__']] = patch_git_src
        local_git_src['__default__'] = patch_git_src['__url__']
        with open(local_path, 'w') as f:
            f.write(json.dumps(local_git_src, ensure_ascii=False, indent=4))
        print("更新配置成功.")
    except Exception:
        print(f"无法修改本地配置文件：{local_path}")
    finally:
        shutil.rmtree('.arms_tpl_src')


def run_update():
    """
    arms更新配置
    arms update
    """
    local_path = Path.home() / '.arms_config.json'
    try:
        config_json = json.loads(local_path.open(encoding='utf-8').read())
        if '__default__' in config_json:
            config_json = config_json[config_json['__default__']]
        git_url = config_json['__url__']
        pull_config(git_url)
    except Exception:
        print(f"无法读取本地配置文件：{local_path}，请先执行arms config [git_url]")


@add_argument('git_url', help='git源访问链接', required=False)
def run_config(git_url):
    """
    arms配置工具

    arms config [git_url]  新增git源
    arms config            切换git源
    """
    if git_url:
        pull_config(git_url)
    else:
        switch_config()


@add_argument('keyword', help='搜索关键词')
def run_search(keyword):
    """
    项目搜索工具
    arms config [keyword]
    """
    keyword = keyword.lower()
    local_path = Path.home() / '.arms_config.json'
    config_json = json.loads(local_path.open(encoding='utf-8').read())
    if '__default__' in config_json:
        config_json = config_json[config_json['__default__']]
    for name, setting in config_json.items():
        if name.startswith('__'):
            continue
        if keyword == name.lower() or keyword in setting['description'].lower() or keyword in setting.get('keywords', '').lower():
            console.print(f'[bold]{name}[/bold] - {setting["description"]}')


@add_subcommand('version', print_version)
@add_subcommand('init', run_init)
@add_subcommand('patch', run_patch)
@add_subcommand('config', run_config)
@add_subcommand('search', run_search)
@add_subcommand('update', run_update)
@add_subcommand('design', run_design)  # 生成文本并复制
@add_subcommand('codegen', run_codegen)  # 生成文件或修改文件
def entrypoint():
    """
    armstrong
    """
    pass


def main():
    if sys.version_info.major == 2 or sys.version_info.minor < 5:
        alert_and_exit('arms已不再支持python2，请安装python3.5+')
    run(entrypoint)
