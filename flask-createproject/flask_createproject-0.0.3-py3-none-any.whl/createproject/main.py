import os
import re
import sys
import time

import emoji
from colored import fg
from colored import stylize
from halo import Halo
from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape

EMAIL_REGEX = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')


def print_error(msg):
    print(stylize(emoji.emojize(msg, language='alias'), fg('red')))


def is_one_word(user_input: str):
    if len(user_input.split(' ')) != 1:
        print_error(':bangbang:  Input cannot contain spaces, try again')
        return False
    return True


def is_valid_bool(user_input: str):
    if user_input not in ("yes", "no"):
        print_error(':bangbang:  Only ("yes", "no") are valid choices, try again')
        return False
    return True


def is_valid_email(user_input: str):
    if not re.fullmatch(EMAIL_REGEX, user_input):
        print_error(':bangbang:  invalid email, try again')
        return False
    return True


def prompt_user(msg, color='green', wait_input=True, validator=None):
    if wait_input:
        spinner = Halo(text='Loading', spinner='dots')
        print(stylize(emoji.emojize(msg, language='alias'), fg(color)))

        if validator:
            while (user_input := input().strip()) and not validator(user_input):
                continue
        else:
            user_input = input().strip()
        spinner.start()
        time.sleep(0.3)
        spinner.stop()
        return user_input
    print(stylize(emoji.emojize(msg, language='alias'), fg(color)))


def aggregate_user_input(base_path: str):
    prompt_user('Hi there :wave:. Let''s create a new Flask project', wait_input=False)
    prompt_user('I need to set up some values in the setup.py file ...', wait_input=False)
    project_name = prompt_user('What would you like to name the project ? :smiley:', validator=is_one_word)
    project_path = f'{base_path}/{project_name}'
    if os.path.exists(project_path):
        print_error(':x:  Project already exists, see ya :wave:')
        sys.exit(1)
    prompt_user('Good choice ! :thumbs_up:', 'blue', wait_input=False)
    main_package = prompt_user('What would you like to name the main package ?', validator=is_one_word)
    author_name = prompt_user('Sorry ! I didn''t catch your name ?')
    author_email = prompt_user('If someone needs to contact you, what would your email be ?', validator=is_valid_email)
    prompt_user('You cannot get nice emails like that anymore :fire:', wait_input=False)
    short_description = prompt_user('How would you shortly describe our new project ? :sunglasses:')
    include_templates = prompt_user(
        'Are you planning on having templates in your project ? (yes/no)', validator=is_valid_bool)
    include_templates = include_templates == 'yes'

    return {
        'project_name': project_name,
        'main_package': main_package,
        'author_name': author_name,
        'author_email': author_email,
        'short_description': short_description,
        'include_templates': include_templates,
    }


def touch(fname):
    if os.path.exists(fname):
        os.utime(fname, None)
    else:
        open(fname, 'a').close()


def get_base_path():
    """

    Can be mocked for testing purposes.
    """
    return '.'


def run():
    base_path = get_base_path()
    setup_data = aggregate_user_input(base_path)
    env = Environment(
        loader=PackageLoader('createproject'),
        autoescape=select_autoescape()
    )
    project_path = os.path.join(base_path, setup_data['project_name'])
    main_pkg = os.path.join(project_path, 'src', setup_data['main_package'])
    os.makedirs(main_pkg, exist_ok=False)
    touch(os.path.join(main_pkg, '__init__.py'))
    if setup_data['include_templates']:
        os.makedirs(os.path.join(main_pkg, 'templates'), exist_ok=False)
        os.makedirs(os.path.join(main_pkg, 'templates', '__init__.py'), exist_ok=False)
    os.makedirs(os.path.join(base_path, setup_data['project_name'], 'tests'), exist_ok=False)

    for filename, parent_dir, data in (
        ('LICENSE', project_path, {}),
        ('.gitignore', project_path, {}),
        ('setup.py', project_path, setup_data),
        ('setup.cfg', project_path, {}),
        ('requirements.txt', project_path, {}),
        ('README.md', project_path, {}),
        ('pyproject.toml', project_path, {}),
        ('MANIFEST.in', project_path, {'include_templates': setup_data['include_templates']}),
        ('__init__.py', main_pkg, {'main_package': setup_data['main_package']}),
    ):
        template_file = env.get_template(f'{filename}.tmpl')
        rendered = template_file.render(**data)
        with open(os.path.join(parent_dir, filename), 'w') as file:
            file.write(rendered)

    prompt_user('Everything is ready :sunglasses: enjoy coding !', wait_input=False)
